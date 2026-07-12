from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.action_models import ActionApproval, ActionLog
from datetime import datetime, timezone

class ActionApprovalService:
    @classmethod
    async def create_approval_request(cls, db: AsyncSession, action_log_id: str, user_id: str) -> ActionApproval:
        approval = ActionApproval(
            action_log_id=action_log_id,
            user_id=user_id,
            status="pending"
        )
        db.add(approval)
        await db.commit()
        await db.refresh(approval)
        return approval

    @classmethod
    async def decide_approval(cls, db: AsyncSession, approval_id: str, approve: bool) -> bool:
        result = await db.execute(select(ActionApproval).where(ActionApproval.id == approval_id))
        approval = result.scalar_one_or_none()
        if not approval or approval.status != "pending":
            return False
            
        approval.status = "approved" if approve else "rejected"
        approval.decided_at = datetime.now(timezone.utc)
        
        # Selectively update linked ActionLog approval status parameter
        log_res = await db.execute(select(ActionLog).where(ActionLog.id == approval.action_log_id))
        log = log_res.scalar_one_or_none()
        if log:
            log.approval_status = "approved" if approve else "rejected"
            if approve:
                from app.services.action_execution_service import ActionExecutionService
                await ActionExecutionService.execute_log_action(db, log)
                return True
            else:
                log.status = "failed"
                log.error_message = "Rejected by user approval decision."
            
        await db.commit()
        return True
