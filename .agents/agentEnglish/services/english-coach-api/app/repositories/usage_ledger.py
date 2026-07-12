import datetime
from sqlalchemy import select, func
from app.repositories.base import BaseDBRepository
from app.db.models import UsageLedger

class UsageLedgerRepository(BaseDBRepository[UsageLedger]):
    """DB-backed repository auditing usage entries, input/output tokens, and dollar expenditures."""

    def __init__(self, db):
        super().__init__(db, UsageLedger)

    async def get_monthly_spend(self, tenant_id: str) -> float:
        """Sums estimated token costs incurred by a tenant within the current calendar month."""
        now = datetime.datetime.utcnow()
        start_of_month = datetime.datetime(now.year, now.month, 1)

        stmt = select(func.sum(self.model_cls.cost_usd)).filter(
            self.model_cls.tenant_id == tenant_id,
            self.model_cls.created_at >= start_of_month
        )
        res = await self.db.execute(stmt)
        cost = res.scalar()
        return float(cost) if cost is not None else 0.0
