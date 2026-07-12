import pytest
import jwt
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant, UsageLedger
from app.repositories.tenants import TenantsRepository
from app.repositories.usage_ledger import UsageLedgerRepository

client = TestClient(app)

@pytest.mark.anyio
async def test_budget_guard_limit_blocks():
    """Asserts that budget breaches return HTTP 402 error."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    
    tenant_id = f"tenant-budget-{uuid.uuid4()}"
    try:
        # 1. Create a tenant with small monthly budget cap
        async with AsyncSessionLocal() as db:
            tenant_repo = TenantsRepository(db)
            ledger_repo = UsageLedgerRepository(db)
            
            tenant = Tenant(
                id=tenant_id,
                name="Budget Tenant",
                org_id="default_org",
                plan_tier="free",
                monthly_budget_usd=1.0  # $1.0 limit
            )
            await tenant_repo.create(tenant)
            
            # 2. Add usage ledger entry exceeding the budget cap
            ledger = UsageLedger(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                product_id="english_coach",
                user_id="user_test",
                cost_usd=2.0  # Exceeds $1.0 budget cap
            )
            await ledger_repo.create(ledger)
            await db.commit()

        # 3. Request should return 402
        token = jwt.encode(
            {"sub": "user_123", "role": "user", "tenant_id": tenant_id},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        res = client.post(
            "/v1/coach/respond",
            json={"text": "network issue tha"},
            headers=headers
        )
        assert res.status_code == 402
        assert "Monthly spending limit" in res.json()["detail"]

    finally:
        settings.AUTH_ENABLED = old_auth_state
