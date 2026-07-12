import base64
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    """Mock speech-to-text (STT) transcription service.
    
    Interfaces with Whisper or Cloud Speech APIs in V2.
    """

    async def transcribe_audio_base64(self, audio_base64: str) -> str:
        """Decodes base64 bytes and returns transcription string text.
        
        Outputs:
            Mocked transcription string.
        """
        logger.info("Transcribing audio payload (base64)")
        if not audio_base64:
            return ""
            
        # Return a default mock Hinglish phrase for unit testing transcription chains
        return "i am not able to join because network issue tha"
