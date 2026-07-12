import pytest
import jwt
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_family_console_admin_endpoints():
    """Asserts that family profiles, checkins list, and saving checks match scope bounds."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    try:
        # Create token
        token = jwt.encode(
            {"sub": "admin_user", "role": "admin", "tenant_id": "tenant_console"},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Save family profile
        res = client.post(
            "/v1/admin/family-console/profiles",
            json={"user_id": "mom_profile", "parent_name": "Mom", "preferred_language": "Hindi"},
            headers=headers
        )
        assert res.status_code == 200
        assert "profile_id" in res.json()

        # 2. List family profiles
        res = client.get("/v1/admin/family-console/profiles", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) >= 1
        assert res.json()[0]["parent_name"] == "Mom"

        # 3. Trigger check-in
        res = client.post(
            "/v1/admin/family-console/checkin",
            json={"user_id": "mom_profile", "message_text": "Main bilkul thik hoon, beta."},
            headers=headers
        )
        assert res.status_code == 200
        assert res.json()["checkin_status"] == "normal"

        # 4. List check-in histories
        res = client.get("/v1/admin/family-console/checkins", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) >= 1

    finally:
        settings.AUTH_ENABLED = old_auth_state
