from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.services.voice_service import VoiceService
from app.api.deps import get_coach_service # to trigger lazy dependency injections if needed
# We will write get_voice_service in deps.py
# Let's import it from deps.py
from app.api.deps import get_voice_service

router = APIRouter()

class VoiceRequest(BaseModel):
    """Audio check request payload containing base64 speech stream."""
    audio_base64: str = Field(..., description="Base64 encoded audio bytes payload.")

class VoiceResponse(BaseModel):
    """Voice check response payload containing transcription and audio answer streams."""
    transcribed_text: str = Field(..., description="Speech transcribed query string.")
    response_text: str = Field(..., description="Coached output reply text.")
    audio_base64: str = Field(..., description="Base64 encoded output speech audio reply.")
    latency_ms: float = Field(..., description="Response latency measured in milliseconds.")

@router.post(
    "/voice/respond",
    response_model=VoiceResponse,
    summary="Evaluate speech audio check-in streams"
)
async def voice_respond(
    request: VoiceRequest,
    service: VoiceService = Depends(get_voice_service)
) -> VoiceResponse:
    """Processes spoken audio, returns text corrections, and synthesizes speech responses."""
    try:
        res_data = await service.process_voice_request(request.audio_base64)
        return VoiceResponse(**res_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while routing speech request parameters: {str(e)}"
        )
