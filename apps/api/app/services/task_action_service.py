import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.goals import Goal
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("task_action_service")

class TaskActionService:
    @classmethod
    async def create_task(
        cls,
        db: AsyncSession,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        target_date: Optional[datetime] = None
    ) -> Goal:
        """
        Creates a new task/goal.
        """
        task = Goal(
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            target_date=target_date,
            progress=0,
            status="pending",
            pinned=False
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        logger.info(f"Created task: {task.id} for user: {user_id}")
        return task

    @classmethod
    async def get_task(cls, db: AsyncSession, task_id: str) -> Optional[Goal]:
        """
        Gets a task by ID.
        """
        stmt = select(Goal).where(Goal.id == task_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def list_tasks(cls, db: AsyncSession, user_id: str) -> List[Goal]:
        """
        Lists all tasks/goals for a user.
        """
        stmt = select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def update_task_status(
        cls,
        db: AsyncSession,
        task_id: str,
        status: str,
        progress: int = 0
    ) -> Optional[Goal]:
        """
        Updates task status and progress metrics.
        """
        task = await cls.get_task(db, task_id)
        if not task:
            return None

        task.status = status
        task.progress = progress
        db.add(task)
        await db.commit()
        await db.refresh(task)
        logger.info(f"Updated task: {task_id} status to {status}")
        return task
