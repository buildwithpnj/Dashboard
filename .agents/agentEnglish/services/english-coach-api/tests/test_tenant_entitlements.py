import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models import ProductEntitlement
from app.repositories.tenants import ProductEntitlementsRepository

@pytest.mark.anyio
async def test_tenant_product_entitlement_gating():
    """Asserts that product entitlements are saved, resolved, and check states correctly."""
    async with AsyncSessionLocal() as db:
        repo = ProductEntitlementsRepository(db)
        
        tenant_id = f"tenant-gate-{uuid.uuid4()}"
        
        # 1. Create a disabled entitlement for lifeos_coach
        ent = ProductEntitlement(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            product_id="lifeos_coach",
            is_active=False
        )
        await repo.create(ent)
        await db.commit()

        # 2. Resolve entitlement
        resolved = await repo.get_by_tenant_and_product(tenant_id, "lifeos_coach")
        assert resolved is not None
        assert resolved.is_active is False

        # Cleanup
        await repo.delete(resolved)
        await db.commit()
