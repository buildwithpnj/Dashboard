import logging
from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ErrorCluster

logger = logging.getLogger(__name__)

class ErrorClustersRepository:
    """Manages SQL operations over error clusters grouping evaluation failures."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, cluster: ErrorCluster) -> None:
        """Saves a new error cluster count record."""
        self.db.add(cluster)
        await self.db.flush()

    async def get_by_run(self, run_id: str) -> List[ErrorCluster]:
        """Retrieves all error clusters created for a specific run ID."""
        stmt = select(ErrorCluster).where(ErrorCluster.run_id == run_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_aggregated(self, run_id: str) -> List[Dict[str, Any]]:
        """Returns error categories aggregate counts sorted descending."""
        stmt = (
            select(
                ErrorCluster.bucket_name,
                ErrorCluster.count,
                ErrorCluster.dataset_name,
                ErrorCluster.model_name
            )
            .where(ErrorCluster.run_id == run_id)
            .order_by(ErrorCluster.count.desc())
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [
            {
                "bucket_name": r[0],
                "count": r[1],
                "dataset_name": r[2],
                "model_name": r[3]
            }
            for r in rows
        ]
