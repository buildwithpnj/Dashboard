import logging
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import HardNegativeExample

logger = logging.getLogger(__name__)


class HardNegativeExamplesRepository:
    """Manages persistence of hard-negative examples for contrast training sets."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, example: HardNegativeExample) -> None:
        """Inserts a new hard-negative example record."""
        self.db.add(example)
        await self.db.flush()

    async def create_batch(self, examples: List[HardNegativeExample]) -> None:
        """Inserts a batch of hard-negative examples efficiently."""
        self.db.add_all(examples)
        await self.db.flush()

    async def get_by_product(self, product_id: str, tenant_id: str = "default_tenant") -> List[HardNegativeExample]:
        """Retrieves all hard-negative examples for a product within a tenant."""
        stmt = (
            select(HardNegativeExample)
            .where(
                HardNegativeExample.product_id == product_id,
                HardNegativeExample.tenant_id == tenant_id
            )
            .order_by(HardNegativeExample.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_error_bucket(self, bucket: str, tenant_id: str = "default_tenant") -> List[HardNegativeExample]:
        """Retrieves hard-negatives filtered by error bucket type."""
        stmt = (
            select(HardNegativeExample)
            .where(
                HardNegativeExample.error_bucket == bucket,
                HardNegativeExample.tenant_id == tenant_id
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_bucket(self, tenant_id: str = "default_tenant") -> dict:
        """Returns counts grouped by error bucket."""
        stmt = select(HardNegativeExample).where(HardNegativeExample.tenant_id == tenant_id)
        result = await self.db.execute(stmt)
        examples = list(result.scalars().all())
        counts = {}
        for ex in examples:
            counts[ex.error_bucket] = counts.get(ex.error_bucket, 0) + 1
        return counts
