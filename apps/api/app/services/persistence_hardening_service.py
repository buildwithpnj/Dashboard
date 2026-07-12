from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.governance import PreviewSession
from typing import Dict, Any

class PersistenceHardeningService:
    @classmethod
    async def cleanup_expired_sessions(cls, db: AsyncSession) -> int:
        """Deletes all preview sessions older than 24 hours. Returns deleted count."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Select target sessions
        result = await db.execute(
            select(PreviewSession).where(PreviewSession.created_at < cutoff)
        )
        sessions = result.scalars().all()
        count = len(sessions)
        
        if count > 0:
            for s in sessions:
                await db.delete(s)
            await db.commit()
            
        return count

    @classmethod
    def validate_chat_artifact(cls, payload: Dict[str, Any]) -> bool:
        """Validates schema structure of any saved chat artifacts."""
        required_keys = ["message", "status"]
        if not all(k in payload for k in required_keys):
            return False
        if not isinstance(payload["message"], str) or not isinstance(payload["status"], str):
            return False
        return True
