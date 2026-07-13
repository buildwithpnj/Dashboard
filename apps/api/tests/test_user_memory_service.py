import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.user_memory_service import UserMemoryService
from app.models.user_profile_memory import UserProfileMemory

@pytest.mark.asyncio
async def test_get_profile_default():
    db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_res
    
    # Trigger get profile (will create default)
    profile = await UserMemoryService.get_profile(db, "user_123")
    assert profile.user_id == "user_123"
    assert profile.tone == "professional"
    assert profile.preferred_language == "English"
    assert db.add.called

@pytest.mark.asyncio
async def test_update_profile_success():
    db = AsyncMock()
    existing_profile = UserProfileMemory(
        user_id="user_123",
        tone="professional",
        explanation_style="detailed"
    )
    
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = existing_profile
    db.execute.return_value = mock_res
    
    updates = {
        "tone": "concise",
        "explanation_style": "brief",
        "goals": ["master prepositions"]
    }
    
    profile = await UserMemoryService.update_profile(db, "user_123", updates)
    assert profile.tone == "concise"
    assert profile.explanation_style == "brief"
    assert profile.goals == ["master prepositions"]
