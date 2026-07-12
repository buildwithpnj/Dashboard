from typing import List
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import Message

class MessagesRepository(BaseDBRepository[Message]):
    """DB-backed storage repository managing conversation messages logs."""

    def __init__(self, db):
        super().__init__(db, Message)

    async def get_by_session(self, session_id: str, limit: int = 50) -> List[Message]:
        """Loads message items chronological log matching a target session identifier."""
        stmt = select(self.model_cls).filter(
            self.model_cls.session_id == session_id
        ).order_by(self.model_cls.created_at.asc()).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
