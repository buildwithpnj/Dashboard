from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.governance import AccessRequest
from app.models.user import User
from typing import List, Dict, Any, Optional

class AccessGovernanceService:
    @classmethod
    async def create_request(cls, db: AsyncSession, name: str, email: str, reason: str) -> AccessRequest:
        req = AccessRequest(name=name, email=email, reason=reason, status="pending")
        db.add(req)
        await db.commit()
        await db.refresh(req)
        return req

    @classmethod
    async def approve_request(cls, db: AsyncSession, request_id: str) -> bool:
        result = await db.execute(select(AccessRequest).where(AccessRequest.id == request_id))
        req = result.scalar_one_or_none()
        if not req:
            return False
        
        req.status = "approved"
        
        # Check if user already registered. If yes, upgrade their role to approved_user.
        user_result = await db.execute(select(User).where(User.email == req.email))
        user = user_result.scalar_one_or_none()
        if user:
            user.role = "approved_user"
            
        await db.commit()
        return True

    @classmethod
    async def reject_request(cls, db: AsyncSession, request_id: str) -> bool:
        result = await db.execute(select(AccessRequest).where(AccessRequest.id == request_id))
        req = result.scalar_one_or_none()
        if not req:
            return False
        req.status = "rejected"
        await db.commit()
        return True

    @classmethod
    async def list_requests(cls, db: AsyncSession) -> List[AccessRequest]:
        result = await db.execute(select(AccessRequest).order_by(AccessRequest.created_at.desc()))
        return list(result.scalars().all())
