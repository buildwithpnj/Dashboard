from typing import List
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import FeedbackExample

class FeedbackExamplesRepository(BaseDBRepository[FeedbackExample]):
    """DB-backed repository managing learning flywheel training datasets."""

    def __init__(self, db):
        super().__init__(db, FeedbackExample)

    async def get_examples_by_status(
        self,
        tenant_id: str,
        product_id: str,
        status: str = "positive",
        limit: int = 5
    ) -> List[FeedbackExample]:
        """Loads training examples filtered by tenant and approval status."""
        stmt = select(self.model_cls).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.product_id == product_id,
            self.model_cls.status == status
        ).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
