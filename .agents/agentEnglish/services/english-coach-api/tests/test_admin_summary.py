import pytest
import jwt
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_admin_summaries_and_alerts():
    """Asserts that configuration and operational alerts check limits function."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    try:
        # Create token
        token = jwt.encode(
            {"sub": "admin_123", "role": "admin", "tenant_id": "tenant_test"},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # 1. System summary
        res = client.get("/v1/admin/system-summary", headers=headers)
        assert res.status_code == 200
        assert "provider" in res.json()

        # 2. Task runs list
        res = client.get("/v1/admin/task-runs", headers=headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

        # 3. Eval summary
        res = client.get("/v1/admin/eval-summary", headers=headers)
        assert res.status_code == 200

        # 4. Alerts
        res = client.get("/v1/admin/alerts", headers=headers)
        assert res.status_code == 200
        assert "status" in res.json()

    finally:
        settings.AUTH_ENABLED = old_auth_state
