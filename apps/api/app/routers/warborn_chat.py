from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.deps import CurrentUser, DB
from app.services.agent_english_service import AgentEnglishService
from app.services.warborn_session_service import WarbornSessionService

router = APIRouter(prefix="/api/warborn", tags=["Warborn Chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    message: str
    status: str

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, current_user: CurrentUser):
    # Enforce role entitlements gating
    if current_user.role not in ["approved_user", "internal_admin"]:
        raise HTTPException(status_code=403, detail="System access pending approval.")

    # Verify session ownership/permissions
    session = WarbornSessionService.get_session(req.session_id)
    if not session or session["user_id"] != current_user.id:
        # Create a new session on demand for logged in user if not present
        sess_id = WarbornSessionService.create_session(current_user.id)
        req.session_id = sess_id
        
    res = await AgentEnglishService.respond_to_authenticated(
        session_id=req.session_id,
        message=req.message
    )
    
    return ChatResponse(
        message=res["message"],
        status=res["status"]
    )
