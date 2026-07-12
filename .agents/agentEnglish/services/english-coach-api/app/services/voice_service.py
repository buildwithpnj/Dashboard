import time
import logging
from typing import Dict, Any

from app.services.transcription_service import TranscriptionService
from app.services.tts_service import TTSService
from app.products.english_coach.service import EnglishCoachService
from app.products.english_coach.schemas import CoachRespondRequest

logger = logging.getLogger(__name__)

class VoiceService:
    """Chains STT, coach text processing, and TTS synthesis into a voice flow."""

    def __init__(
        self,
        transcription_service: TranscriptionService,
        tts_service: TTSService,
        coach_service: EnglishCoachService
    ):
        self.transcription_service = transcription_service
        self.tts_service = tts_service
        self.coach_service = coach_service

    async def process_voice_request(self, audio_base64: str, user_id: str = "default_user") -> Dict[str, Any]:
        """Transcribes input audio, runs coaching correction, synthesizes output audio."""
        start_time = time.perf_counter()

        # 1. Transcribe voice input to text
        transcribed_text = await self.transcription_service.transcribe_audio_base64(audio_base64)
        if not transcribed_text:
            transcribed_text = "No audio detected."

        # 2. Evaluate text query through English Coach service
        coach_req = CoachRespondRequest(
            text=transcribed_text,
            session_id=f"voice-session-{str(time.time())[:8]}"
        )
        coach_res = await self.coach_service.process_request(coach_req)

        # Decide output speech text
        if coach_res.ambiguity:
            response_text = coach_res.clarification_question
        else:
            response_text = coach_res.natural_english if coach_res.natural_english else "I could not understand that request."

        # 3. Synthesize reply text back to speech audio
        audio_out = await self.tts_service.synthesize_text_to_speech(response_text)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "transcribed_text": transcribed_text,
            "response_text": response_text,
            "audio_base64": audio_out,
            "latency_ms": latency_ms
        }
