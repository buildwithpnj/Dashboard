from typing import Optional, List
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import Session

class SessionsRepository(BaseDBRepository[Session]):
    """DB-backed storage repository managing user-chat session durations and activities."""

    def __init__(self, db):
        super().__init__(db, Session)

    async def get_active_by_user_and_product(
        self,
        user_id: str,
        product_id: str,
        tenant_id: str = "default_tenant"
    ) -> Optional[Session]:
        """Fetches the latest active session record matching user, product, and tenant targets."""
        stmt = select(self.model_cls).filter(
            self.model_cls.user_id == user_id,
            self.model_cls.product_id == product_id,
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.is_active == True
        ).order_by(self.model_cls.created_at.desc())
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_all_by_user(self, user_id: str, tenant_id: str = "default_tenant") -> List[Session]:
        """Returns all sessions tracked for a user within a tenant scope."""
        stmt = select(self.model_cls).filter(
            self.model_cls.user_id == user_id,
            self.model_cls.tenant_id == tenant_id
        ).order_by(self.model_cls.created_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
