from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from app.deps import DB
from app.models.governance import PreviewSession
from app.repositories.preview_events import PreviewEventsRepository
from app.services.agent_english_service import AgentEnglishService
from app.services.admin_controls_service import AdminControlsService
from app.services.rollout_flag_service import RolloutFlagService

# Import security, observability, and fallback components
from app.security.jailbreak_detector import JailbreakDetector
from app.security.spam_pattern_detector import SpamPatternDetector
from app.security.anomaly_scorer import AnomalyScorer
from app.security.session_cooldown import SessionCooldown
from app.services.preview_fallback_service import PreviewFallbackService
from app.services.preview_timeout_handler import PreviewTimeoutHandler
from app.observability.preview_tracing import PreviewTracing
import sys
import os

agents_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.agents"))
if agents_path not in sys.path:
    sys.path.insert(0, agents_path)

from agentEnglish.runtime import classify_intent

router = APIRouter(prefix="/api/public-preview", tags=["Public Preview"])

class SessionResponse(BaseModel):
    session_id: str

class MessageRequest(BaseModel):
    session_id: str
    message: str

class MessageResponse(BaseModel):
    message: str
    status: str

@router.post("/session", response_model=SessionResponse)
async def start_session(request: Request, db: DB):
    ip_address = request.client.host if request.client else "unknown"
    session = PreviewSession(ip_address=ip_address, turns=0, tokens=0, cost=0.0, active=True)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionResponse(session_id=session.id)

@router.post("/respond", response_model=MessageResponse)
async def get_response(req: MessageRequest, db: DB):
    # 1. Global Kill Switch Check
    if await AdminControlsService.is_preview_disabled(db):
        return MessageResponse(
            message="Preview service is currently disabled by administrators.",
            status="blocked"
        )

    # 2. Fetch session from Database
    result = await db.execute(select(PreviewSession).where(PreviewSession.id == req.session_id))
    session = result.scalar_one_or_none()
    if not session or not session.active:
        raise HTTPException(status_code=400, detail="Invalid session token.")
        
    # 3. Cooldown checks
    if SessionCooldown.is_cooling_down(req.session_id):
        fallback_msg = PreviewFallbackService.get_fallback("cooldown")
        return MessageResponse(message=fallback_msg, status="blocked")
        
    # 4. Anomaly scoring
    anomaly_score = AnomalyScorer.score_request(req.session_id)
    if anomaly_score >= 1.0:
        SessionCooldown.apply_cooldown(req.session_id)
        fallback_msg = PreviewFallbackService.get_fallback("cooldown")
        return MessageResponse(message=fallback_msg, status="blocked")

    # 5. Staged Rollout checks
    in_rollout = await RolloutFlagService.is_session_in_rollout(db, req.session_id)
    if not in_rollout:
        return MessageResponse(
            message="Preview access is restricted at this time.",
            status="blocked"
        )

    # 6. Spam checks
    if SpamPatternDetector.is_spam(req.message):
        fallback_msg = PreviewFallbackService.get_fallback("abuse_blocked")
        return MessageResponse(message=fallback_msg, status="blocked")

    # 7. Jailbreak checks
    if JailbreakDetector.is_jailbreak(req.message):
        fallback_msg = PreviewFallbackService.get_fallback("abuse_blocked")
        return MessageResponse(message=fallback_msg, status="blocked")

    # 8. Disabled Intent check
    intent = await classify_intent(req.message)
    disabled_intents = await AdminControlsService.get_disabled_intents(db)
    if intent in disabled_intents:
        fallback_msg = PreviewFallbackService.get_fallback("unsupported_intent")
        return MessageResponse(message=fallback_msg, status="blocked")

    # 9. Quota Checks (Dynamic cap values)
    token_cap_str = await AdminControlsService.get_config(db, "preview_token_cap", "2000")
    try:
        token_cap = int(token_cap_str)
    except ValueError:
        token_cap = 2000

    if session.turns >= 5:
        fallback_msg = PreviewFallbackService.get_fallback("budget_exhausted")
        return MessageResponse(message=fallback_msg, status="blocked")
        
    if session.tokens >= token_cap:
        fallback_msg = PreviewFallbackService.get_fallback("budget_exhausted")
        return MessageResponse(message=fallback_msg, status="blocked")

    # 10. Initialize Tracing
    trace = PreviewTracing.start_trace(req.session_id, req.message)
    
    try:
        # Wrap model response call inside timeout execution handler
        PreviewTracing.record_model_start(trace)
        
        async def _call():
            return await AgentEnglishService.respond_to_preview(
                session_id=req.session_id, 
                message=req.message
            )
            
        res = await PreviewTimeoutHandler.execute_with_timeout(_call)
        
        PreviewTracing.record_model_end(trace, res["tokens_used"], res["cost"])
        
        # Log event log in memory database
        PreviewEventsRepository.log_event(
            session_id=req.session_id,
            prompt=req.message,
            response=res["message"],
            tokens=res["tokens_used"],
            cost=res["cost"],
            status=res["status"]
        )
        
        blocked_reason = None
        if res["status"] == "blocked":
            blocked_reason = "internal_guardrail_budget_exhausted"
            
        PreviewTracing.end_trace(trace, res["status"], blocked_reason=blocked_reason, intent=intent)
        
        # Save to database preview session stats
        session.turns += 1
        session.tokens += res["tokens_used"]
        session.cost += res["cost"]
        await db.commit()

        return MessageResponse(
            message=res["message"],
            status=res["status"]
        )
        
    except TimeoutError:
        PreviewTracing.end_trace(trace, "error", blocked_reason="timeout", is_timeout=True)
        fallback_msg = PreviewFallbackService.get_fallback("timeout")
        return MessageResponse(message=fallback_msg, status="error")
    except Exception as err:
        PreviewTracing.end_trace(trace, "error", blocked_reason=str(err))
        return MessageResponse(message="Service currently unavailable.", status="error")
