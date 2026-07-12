import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from .admin_controls_service import AdminControlsService

class RolloutFlagService:
    @classmethod
    async def is_session_in_rollout(cls, db: AsyncSession, identifier: str) -> bool:
        """Determines if user session falls inside the active staged rollout percentage."""
        # 1. Fetch rollout percentage limit from DB config (default to 100%)
        pct_str = await AdminControlsService.get_config(db, "staged_rollout_pct", "100")
        try:
            pct = int(pct_str)
        except ValueError:
            pct = 100

        if pct >= 100:
            return True
        if pct <= 0:
            return False

        # 2. Hash session identifier to deterministically return value between 0 and 99
        hash_val = int(hashlib.md5(identifier.encode("utf-8")).hexdigest(), 16)
        bucket = hash_val % 100
        return bucket < pct
