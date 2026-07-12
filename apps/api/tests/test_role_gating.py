import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.routers.warborn_chat import chat, ChatRequest
from app.models.user import User

def test_role_gating_unapproved():
    # User with a role not in approved_user or internal_admin should be blocked
    user = User(email="test@example.com", role="anonymous_preview")
    
    # We expect HTTP 403 error to be raised when a user is not authorized
    with pytest.raises(HTTPException) as exc_info:
        # Inline mock dependencies inside the handler
        import asyncio
        asyncio.run(chat(
            req=ChatRequest(message="hello", session_id="sess_123"),
            current_user=user
        ))
    assert exc_info.value.status_code == 403
    assert "access pending" in exc_info.value.detail.lower()
