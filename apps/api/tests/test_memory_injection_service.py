import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.memory_injection_service import MemoryInjectionService
from app.services.session_memory_service import SessionMemoryService
from app.models.user_profile_memory import UserProfileMemory

@pytest.mark.asyncio
async def test_memory_injection_structure():
    db = AsyncMock()
    
    # Mock retrieval profile
    profile = UserProfileMemory(
        user_id="user_123",
        tone="concise",
        preferred_language="English",
        weaknesses=["tense consistency"],
        goals=["clear emails"]
    )
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = profile
    db.execute.return_value = mock_res
    
    # Set session preference
    SessionMemoryService.set_session_preference("sess_555", "mode", "debug")
    
    # Run injection
    injected = await MemoryInjectionService.inject_memories_into_system_prompt(
        db=db,
        user_id="user_123",
        query="practice writing clear emails",
        session_id="sess_555",
        base_prompt="You are an assistant."
    )
    
    assert "USER MEMORY GATEWAY" in injected
    assert "Preferred interaction tone: concise" in injected
    assert "User's active goal matching query context: clear emails" in injected
    assert "Session preference - mode: debug" in injected
    assert "You are an assistant." in injected
    
    # Cleanup session
    SessionMemoryService.clear_session("sess_555")
