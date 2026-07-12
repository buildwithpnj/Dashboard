from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.repositories.preview_sessions import PreviewSessionsRepository
from app.repositories.preview_events import PreviewEventsRepository
from app.services.agent_english_service import AgentEnglishService

# Import security, observability, and fallback components
from app.security.jailbreak_detector import JailbreakDetector
from app.security.spam_pattern_detector import SpamPatternDetector
from app.security.anomaly_scorer import AnomalyScorer
from app.security.session_cooldown import SessionCooldown
from app.services.preview_fallback_service import PreviewFallbackService
from app.services.preview_timeout_handler import PreviewTimeoutHandler
from app.observability.preview_tracing import PreviewTracing

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
async def start_session(request: Request):
    ip_address = request.client.host if request.client else "unknown"
    session_id = PreviewSessionsRepository.create_session(ip_address)
    return SessionResponse(session_id=session_id)

@router.post("/respond", response_model=MessageResponse)
async def get_response(req: MessageRequest):
    session = PreviewSessionsRepository.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session token.")
        
    # 1. Cooldown checks
    if SessionCooldown.is_cooling_down(req.session_id):
        fallback_msg = PreviewFallbackService.get_fallback("cooldown")
        return MessageResponse(message=fallback_msg, status="blocked")
        
    # 2. Anomaly scoring
    anomaly_score = AnomalyScorer.score_request(req.session_id)
    if anomaly_score >= 1.0:
        SessionCooldown.apply_cooldown(req.session_id)
        fallback_msg = PreviewFallbackService.get_fallback("cooldown")
        return MessageResponse(message=fallback_msg, status="blocked")

    # 3. Spam checks
    if SpamPatternDetector.is_spam(req.message):
        fallback_msg = PreviewFallbackService.get_fallback("abuse_blocked")
        return MessageResponse(message=fallback_msg, status="blocked")

    # 4. Jailbreak checks
    if JailbreakDetector.is_jailbreak(req.message):
        fallback_msg = PreviewFallbackService.get_fallback("abuse_blocked")
        return MessageResponse(message=fallback_msg, status="blocked")

    # 5. Initialize Tracing
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
        
        # Log event logs
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
            
        PreviewTracing.end_trace(trace, res["status"], blocked_reason=blocked_reason, intent=None)
        
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
