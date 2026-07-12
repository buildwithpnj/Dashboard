from typing import List, Optional
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import ProductConfig

class ProductConfigsRepository(BaseDBRepository[ProductConfig]):
    """DB-backed storage repository managing prompt templates and budgets configuration mapping."""

    def __init__(self, db):
        super().__init__(db, ProductConfig)

    async def get_active_configs(self) -> List[ProductConfig]:
        """Returns configurations of active products."""
        stmt = select(self.model_cls).filter(self.model_cls.is_active == True)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
