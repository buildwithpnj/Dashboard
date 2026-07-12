import pytest
import base64
from fastapi.testclient import TestClient

def test_voice_endpoint(client):
    """Verifies that the /voice/respond API transcribes, evaluates, and returns speech base64."""
    # Convert dummy bytes to base64 audio payload
    audio_payload = base64.b64encode(b"MOCK_SOUND_WAVE").decode("utf-8")

    payload = {
        "audio_base64": audio_payload
    }

    response = client.post("/v1/coach/voice/respond", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "transcribed_text" in data
    assert "response_text" in data
    assert "audio_base64" in data
    assert "latency_ms" in data

    # Verify mock STT output match
    assert "network issue" in data["transcribed_text"].lower()
    # Verify mock TTS output match
    assert len(data["audio_base64"]) > 0
