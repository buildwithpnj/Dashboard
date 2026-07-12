from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import LearnerProfile

class LearnerProfilesRepository(BaseDBRepository[LearnerProfile]):
    """DB-backed storage repository managing user preferences and profile summaries."""

    def __init__(self, db):
        super().__init__(db, LearnerProfile)

    async def get_by_user_and_product(
        self,
        user_id: str,
        product_id: str,
        tenant_id: str = "default_tenant"
    ) -> Optional[LearnerProfile]:
        """Fetches the unique profile of a user matching the target agent product key and tenant scope."""
        stmt = select(self.model_cls).filter(
            self.model_cls.user_id == user_id,
            self.model_cls.product_id == product_id,
            self.model_cls.tenant_id == tenant_id
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()
