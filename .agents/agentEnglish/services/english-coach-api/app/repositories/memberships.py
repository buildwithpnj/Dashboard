from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import Membership

class MembershipsRepository(BaseDBRepository[Membership]):
    """DB-backed repository mapping user access rights and admin status roles to tenant partitions."""

    def __init__(self, db):
        super().__init__(db, Membership)

    async def get_user_role(self, tenant_id: str, user_id: str) -> Optional[str]:
        """Looks up the authorization role ('admin', 'user') assigned to a user in a tenant."""
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.user_id == user_id
        )
        res = await self.db.execute(stmt)
        membership = res.scalars().first()
        return membership.role if membership else None
