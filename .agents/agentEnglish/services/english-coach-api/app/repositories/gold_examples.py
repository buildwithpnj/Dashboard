import logging
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import GoldExample

logger = logging.getLogger(__name__)


class GoldExamplesRepository:
    """Manages persistence of quality-verified gold training examples with provenance."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, example: GoldExample) -> None:
        """Inserts a new gold example record."""
        self.db.add(example)
        await self.db.flush()

    async def create_batch(self, examples: List[GoldExample]) -> None:
        """Inserts a batch of gold examples efficiently."""
        self.db.add_all(examples)
        await self.db.flush()

    async def get_by_product(self, product_id: str, tenant_id: str = "default_tenant") -> List[GoldExample]:
        """Retrieves all gold examples for a product within a tenant."""
        stmt = (
            select(GoldExample)
            .where(
                GoldExample.product_id == product_id,
                GoldExample.tenant_id == tenant_id,
                GoldExample.review_status == "APPROVED"
            )
            .order_by(GoldExample.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_review(self, tenant_id: str = "default_tenant") -> List[GoldExample]:
        """Retrieves gold examples awaiting human review."""
        stmt = (
            select(GoldExample)
            .where(
                GoldExample.tenant_id == tenant_id,
                GoldExample.review_status == "PENDING"
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def approve(self, example_id: str) -> None:
        """Marks a gold example as approved after human review."""
        stmt = select(GoldExample).where(GoldExample.id == example_id)
        result = await self.db.execute(stmt)
        example = result.scalar_one_or_none()
        if example:
            example.review_status = "APPROVED"

    async def reject(self, example_id: str) -> None:
        """Marks a gold example as rejected."""
        stmt = select(GoldExample).where(GoldExample.id == example_id)
        result = await self.db.execute(stmt)
        example = result.scalar_one_or_none()
        if example:
            example.review_status = "REJECTED"

    async def count_by_status(self, tenant_id: str = "default_tenant") -> dict:
        """Returns counts grouped by review status."""
        stmt = select(GoldExample).where(GoldExample.tenant_id == tenant_id)
        result = await self.db.execute(stmt)
        examples = list(result.scalars().all())
        counts = {}
        for ex in examples:
            counts[ex.review_status] = counts.get(ex.review_status, 0) + 1
        return counts
