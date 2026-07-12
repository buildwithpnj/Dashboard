from typing import List
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import Experiment

class ExperimentsRepository(BaseDBRepository[Experiment]):
    """DB-backed repository managing A/B experiment splits and variant weights."""

    def __init__(self, db):
        super().__init__(db, Experiment)

    async def get_active_experiments(self) -> List[Experiment]:
        """Retrieves all active A/B testing experiment records."""
        stmt = select(self.model_cls).filter(self.model_cls.is_active == True)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
