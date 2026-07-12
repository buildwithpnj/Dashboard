import pytest
import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_admin_metrics_auth_flows():
    """Tests all auth combinations (API keys, JWT, roles, disable switch) on admin metrics route."""
    # Ensure auth settings are enabled during test context
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    
    try:
        # 1. Access without credentials should return 401
        res = client.get("/v1/admin/metrics")
        assert res.status_code == 401
        
        # 2. Access with invalid API key should return 401
        res = client.get("/v1/admin/metrics", headers={"X-API-KEY": "wrong_secret"})
        assert res.status_code == 401
        
        # 3. Access with valid admin API key should succeed (200)
        res = client.get("/v1/admin/metrics", headers={"X-API-KEY": "warborn_admin_secret"})
        assert res.status_code == 200
        assert "total_requests" in res.json()

        # 4. Access with JWT user role token should return 403 (unauthorized role)
        user_token = jwt.encode(
            {"sub": "user_123", "role": "user", "tenant_id": "tenant_1"},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        res = client.get("/v1/admin/metrics", headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 403

        # 5. Access with JWT admin role token should succeed (200)
        admin_token = jwt.encode(
            {"sub": "admin_123", "role": "admin", "tenant_id": "tenant_1"},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        res = client.get("/v1/admin/metrics", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200

    finally:
        # Restore old auth state
        settings.AUTH_ENABLED = old_auth_state

def test_auth_disabled_fallback():
    """Asserts that when AUTH_ENABLED=False, the metrics endpoint skips auth checks."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = False
    try:
        res = client.get("/v1/admin/metrics")
        assert res.status_code == 200
    finally:
        settings.AUTH_ENABLED = old_auth_state
