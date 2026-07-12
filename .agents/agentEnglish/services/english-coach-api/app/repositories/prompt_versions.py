from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import PromptVersion

class PromptVersionsRepository(BaseDBRepository[PromptVersion]):
    """DB-backed repository managing versioned system prompt templates."""

    def __init__(self, db):
        super().__init__(db, PromptVersion)

    async def get_active_version(self, product_id: str, task_id: str) -> Optional[PromptVersion]:
        """Retrieves the active prompt configuration version for a product task."""
        stmt = select(self.model_cls).filter(
            self.model_cls.product_id == product_id,
            self.model_cls.task_id == task_id,
            self.model_cls.is_active == True
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()
