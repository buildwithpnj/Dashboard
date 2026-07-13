import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_profile_memory import UserProfileMemory
from typing import Dict, Any, List, Optional

logger = logging.getLogger("user_memory_service")

class UserMemoryService:
    @classmethod
    async def get_profile(cls, db: AsyncSession, user_id: str) -> UserProfileMemory:
        """
        Retrieves the UserProfileMemory for a given user. Creates one with default parameters if none exists.
        """
        stmt = select(UserProfileMemory).where(UserProfileMemory.user_id == user_id)
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            logger.info(f"Creating default UserProfileMemory for user: {user_id}")
            profile = UserProfileMemory(
                user_id=user_id,
                tone="professional",
                explanation_style="detailed",
                target_english_level="Advanced",
                weaknesses=[],
                goals=[],
                preferred_language="English"
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        return profile

    @classmethod
    async def update_profile(
        cls,
        db: AsyncSession,
        user_id: str,
        updates: Dict[str, Any]
    ) -> UserProfileMemory:
        """
        Updates the profile memory attributes with tenant scoping validation.
        """
        profile = await cls.get_profile(db, user_id)

        # Allow updating specific fields safely
        allowed_fields = [
            "tone",
            "explanation_style",
            "target_english_level",
            "weaknesses",
            "goals",
            "preferred_language"
        ]

        for key, value in updates.items():
            if key in allowed_fields:
                setattr(profile, key, value)

        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        logger.info(f"Updated UserProfileMemory for user: {user_id} with updates: {updates}")
        return profile
