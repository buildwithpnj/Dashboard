import logging
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import EvalExampleResult

logger = logging.getLogger(__name__)


class EvalExamplesRepository:
    """Manages persistence of per-example evaluation results with cost and quality metrics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, example: EvalExampleResult) -> None:
        """Inserts a new eval example result record."""
        self.db.add(example)
        await self.db.flush()

    async def create_batch(self, examples: List[EvalExampleResult]) -> None:
        """Inserts a batch of eval example results efficiently."""
        self.db.add_all(examples)
        await self.db.flush()

    async def get_by_run(self, run_id: str, limit: int = 500) -> List[EvalExampleResult]:
        """Retrieves all example results for a specific eval run."""
        stmt = (
            select(EvalExampleResult)
            .where(EvalExampleResult.run_id == run_id)
            .order_by(EvalExampleResult.created_at)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_score_range(
        self, run_id: str, min_score: float, max_score: float
    ) -> List[EvalExampleResult]:
        """Retrieves examples within a composite score range for a run."""
        stmt = (
            select(EvalExampleResult)
            .where(
                EvalExampleResult.run_id == run_id,
                EvalExampleResult.composite_score >= min_score,
                EvalExampleResult.composite_score <= max_score
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_promotable(self, run_id: str, threshold: float = 0.85) -> List[EvalExampleResult]:
        """Retrieves high-scoring examples eligible for gold promotion."""
        stmt = (
            select(EvalExampleResult)
            .where(
                EvalExampleResult.run_id == run_id,
                EvalExampleResult.composite_score >= threshold,
                EvalExampleResult.status == "SCORED"
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_hard_negatives(self, run_id: str, threshold: float = 0.4) -> List[EvalExampleResult]:
        """Retrieves low-scoring examples for hard-negative dataset creation."""
        stmt = (
            select(EvalExampleResult)
            .where(
                EvalExampleResult.run_id == run_id,
                EvalExampleResult.composite_score < threshold,
                EvalExampleResult.error_bucket.isnot(None)
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_status(self, run_id: str) -> dict:
        """Returns counts grouped by status for a run."""
        stmt = select(EvalExampleResult).where(EvalExampleResult.run_id == run_id)
        result = await self.db.execute(stmt)
        examples = list(result.scalars().all())
        counts = {}
        for ex in examples:
            counts[ex.status] = counts.get(ex.status, 0) + 1
        return counts
