import pytest
import jwt
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.repositories.usage_ledger import UsageLedgerRepository

client = TestClient(app)

@pytest.mark.anyio
async def test_usage_ledger_entries():
    """Asserts that requests write token volumes and estimated costs to usage_ledger."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    try:
        # Generate token
        token = jwt.encode(
            {"sub": "user_meter", "role": "user", "tenant_id": "tenant_meter"},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Dispatch coach respond request
        res = client.post(
            "/v1/coach/respond",
            json={"text": "network issue tha"},
            headers=headers
        )
        assert res.status_code == 200

        # Query usage ledger database
        async with AsyncSessionLocal() as db:
            repo = UsageLedgerRepository(db)
            spend = await repo.get_monthly_spend("tenant_meter")
            assert spend > 0.0

    finally:
        settings.AUTH_ENABLED = old_auth_state
