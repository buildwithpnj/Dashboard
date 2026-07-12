from typing import List, Optional
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import CheckinRun

class CheckinRunsRepository(BaseDBRepository[CheckinRun]):
    """DB-backed storage repository managing wellness check-in runs and manual alerts."""

    def __init__(self, db):
        super().__init__(db, CheckinRun)

    async def get_by_session(self, session_id: str, tenant_id: str = "default_tenant") -> Optional[CheckinRun]:
        """Loads a single run record matching the conversation session and tenant."""
        stmt = select(self.model_cls).filter(
            self.model_cls.session_id == session_id,
            self.model_cls.tenant_id == tenant_id
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_escalated_runs(self, tenant_id: str = "default_tenant") -> List[CheckinRun]:
        """Loads all run entries that triggered wellness escalations under the active tenant."""
        stmt = select(self.model_cls).filter(
            self.model_cls.status == "escalated",
            self.model_cls.tenant_id == tenant_id
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
