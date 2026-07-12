from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from app.models.action_models import ActionLog
from app.services.action_registry import ActionRegistry
from app.services.action_approval_service import ActionApprovalService
from datetime import datetime, timezone

# Import all individual action executers
from app.services.actions.save_corrected_example import SaveCorrectedExampleAction
from app.services.actions.create_lesson_note import CreateLessonNoteAction
from app.services.actions.update_preference import UpdatePreferenceAction
from app.services.actions.mark_pattern_mastered import MarkPatternMasteredAction
from app.services.actions.create_followup_practice import CreateFollowupPracticeAction

class ActionExecutionService:
    @classmethod
    async def request_execution(
        cls, 
        db: AsyncSession, 
        user_id: str, 
        user_role: str, 
        action_name: str, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validates, logs, and triggers or queues action executions based on configurations."""
        # 1. Enforce preview/private boundary
        if user_role not in ["approved_user", "internal_admin"]:
            return {"status": "failed", "error": "Action execution restricted to approved users."}

        # 2. Check Action Registry Definitions
        action = ActionRegistry.get_action(action_name)
        if not action:
            return {"status": "failed", "error": "Action not found."}

        # 3. Validate input schemas parameters
        if not ActionRegistry.validate_inputs(action_name, payload):
            return {"status": "failed", "error": "Input payload schema validation failed."}

        # 4. Check role rights gating
        if user_role not in action["allowed_roles"]:
            return {"status": "failed", "error": "Unauthorized role context."}

        # 5. Create durable execution audit log
        log = ActionLog(
            user_id=user_id,
            action_name=action_name,
            input_payload=payload,
            status="pending",
            approval_status="auto_approved"
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)

        # 6. Check manual approval rules
        if action["requires_approval"]:
            log.approval_status = "pending"
            await db.commit()
            approval = await ActionApprovalService.create_approval_request(db, log.id, user_id)
            return {
                "status": "pending_approval",
                "action_log_id": log.id,
                "approval_id": approval.id,
                "message": "Action execution is pending user approval."
            }

        # 7. Execute immediately (Auto-Approved)
        return await cls.execute_log_action(db, log)

    @classmethod
    async def execute_log_action(cls, db: AsyncSession, log: ActionLog) -> Dict[str, Any]:
        executors: Dict[str, Any] = {
            "save_corrected_example": SaveCorrectedExampleAction,
            "create_lesson_note": CreateLessonNoteAction,
            "update_preference": UpdatePreferenceAction,
            "mark_pattern_mastered": MarkPatternMasteredAction,
            "create_followup_practice": CreateFollowupPracticeAction
        }

        executor = executors.get(log.action_name)
        if not executor:
            log.status = "failed"
            log.error_message = "Executor mapping not found."
            await db.commit()
            return {"status": "failed", "error": log.error_message}

        try:
            res = await executor.execute(db, log.user_id, log.input_payload)
            log.status = "success"
            log.result_payload = res
            log.completed_at = datetime.now(timezone.utc)
            await db.commit()
            return res
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.now(timezone.utc)
            await db.commit()
            return {"status": "failed", "error": log.error_message}
