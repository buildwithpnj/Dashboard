from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import Tenant, ProductEntitlement

class TenantsRepository(BaseDBRepository[Tenant]):
    """DB-backed repository managing SaaS tenant configurations, plan tiers, and monthly caps."""

    def __init__(self, db):
        super().__init__(db, Tenant)

class ProductEntitlementsRepository(BaseDBRepository[ProductEntitlement]):
    """DB-backed repository gating product or coaching entitlements for a tenant."""

    def __init__(self, db):
        super().__init__(db, ProductEntitlement)

    async def get_by_tenant_and_product(self, tenant_id: str, product_id: str) -> Optional[ProductEntitlement]:
        """Fetches the entitlement configuration for a specific product and tenant partition."""
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.product_id == product_id
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()
