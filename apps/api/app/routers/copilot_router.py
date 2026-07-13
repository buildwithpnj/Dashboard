from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional
from app.deps import CurrentUser, DB
from app.schemas.copilot_context_payload import CopilotContextPayload
from app.services.copilot_session_service import CopilotSessionService
from app.services.copilot_router_service import CopilotRouterService
from app.services.ui_action_bridge import UiActionBridge
from app.services.voice_session_service import VoiceSessionService

router = APIRouter(prefix="/api/copilot", tags=["Global Dashboard Copilot"])

@router.post("/chat", status_code=status.HTTP_200_OK)
async def submit_copilot_query(
    query: str,
    ctx: CopilotContextPayload,
    current_user: CurrentUser,
    db: DB
):
    """
    Submits a route-aware copilot chat message and returns response plus action bridge recommendations.
    """
    sess = await CopilotSessionService.get_or_create_session(db, current_user.id)
    
    # Process route & query
    reply_text, action = await CopilotRouterService.process_query(
        db, query, ctx, current_user.id, sess.chat_history
    )
    
    # Save history
    await CopilotSessionService.append_message(db, sess, "user", query)
    await CopilotSessionService.append_message(db, sess, "assistant", reply_text, action)
    
    # Schedule action if triggered
    act_log_id = None
    if action:
        act_log_id = await UiActionBridge.bridge_action_to_runner(
            db, action["action_name"], action["payload"]
        )
        
    return {
        "reply": reply_text,
        "suggested_action": action,
        "action_log_id": act_log_id,
        "session_id": sess.id
    }

@router.post("/voice", status_code=status.HTTP_200_OK)
async def submit_voice_stream(
    ctx: CopilotContextPayload,
    current_user: CurrentUser,
    db: DB
):
    """
    Simulates speech-to-text trigger for voice interaction on current view contexts.
    """
    sess = await CopilotSessionService.get_or_create_session(db, current_user.id)
    
    transcription = VoiceSessionService.transcribe_audio_chunk(b"")
    reply_text, action = await CopilotRouterService.process_query(
        db, transcription, ctx, current_user.id, sess.chat_history
    )
    
    await CopilotSessionService.append_message(db, sess, "user", transcription)
    await CopilotSessionService.append_message(db, sess, "assistant", reply_text, action)
    
    return {
        "transcription": transcription,
        "reply": reply_text,
        "suggested_action": action,
        "session_id": sess.id
    }
