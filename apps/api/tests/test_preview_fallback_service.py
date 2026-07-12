import pytest
from app.services.preview_fallback_service import PreviewFallbackService

def test_fallback_copy_generation():
    assert "safety rules" in PreviewFallbackService.get_fallback("abuse_blocked")
    assert "rate limited" in PreviewFallbackService.get_fallback("cooldown")
    assert "timed out" in PreviewFallbackService.get_fallback("timeout")
