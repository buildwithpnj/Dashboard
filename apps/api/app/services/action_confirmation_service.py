import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.task_action_service import TaskActionService
from app.services.action_result_verifier import ActionResultVerifier
from app.services.task_persistence_guard import TaskPersistenceGuard
from app.services.action_contract_validator import ActionContractValidator
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("action_confirmation_service")

class ActionConfirmationService:
    @classmethod
    async def process_task_creation_with_verification(
        cls,
        db: AsyncSession,
        user_id: str,
        payload: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Executes a task creation with strict schema contract checks and DB persistency verifications.
        Returns (success, message, task_id).
        """
        # 1. Validate Schema
        is_schema_valid, schema_err = ActionContractValidator.validate_create_contract(payload)
        if not is_schema_valid:
            logger.warning(f"Task creation contract validation failed: {schema_err}")
            return False, f"Action schema violation: {schema_err}", None

        # 2. Check Write Constraints
        is_safe, safety_err = TaskPersistenceGuard.validate_write_safety(payload)
        if not is_safe:
            logger.warning(f"Task write safety blocked: {safety_err}")
            return False, f"Action blocked: {safety_err}", None

        title = payload["title"]
        description = payload.get("description")
        category = payload.get("category")

        # 3. Save to DB
        try:
            task = await TaskActionService.create_task(
                db=db,
                user_id=user_id,
                title=title,
                description=description,
                category=category
            )
        except Exception as e:
            logger.error(f"Failed database execution for task: {e}")
            return False, f"Database transaction failure: {e}", None

        # 4. Verify persistency
        is_verified = await ActionResultVerifier.verify_task_created(db, task.id)
        if not is_verified:
            return False, "Database save failed verification check. State was rolled back.", None

        return True, f"Successfully created task '{title}' with ID {task.id}.", task.id
