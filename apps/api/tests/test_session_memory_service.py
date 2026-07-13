import pytest
from app.services.session_memory_service import SessionMemoryService

def test_session_preference_flow():
    session_id = "sess_999"
    SessionMemoryService.clear_session(session_id)

    # Set pref
    SessionMemoryService.set_session_preference(session_id, "style", "conversational")
    assert SessionMemoryService.get_session_preference(session_id, "style") == "conversational"

    # Get all
    prefs = SessionMemoryService.get_all_session_preferences(session_id)
    assert prefs == {"style": "conversational"}

    # Clear
    SessionMemoryService.clear_session(session_id)
    assert SessionMemoryService.get_session_preference(session_id, "style") is None
