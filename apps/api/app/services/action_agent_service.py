import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.action_confirmation_service import ActionConfirmationService
from typing import Dict, Any, Tuple

logger = logging.getLogger("action_agent")

class ActionAgentService:
    @classmethod
    async def execute_action(
        cls,
        db: AsyncSession,
        user_id: str,
        action_name: str,
        payload: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Executes verified actions.
        """
        logger.info(f"ActionAgent executing action: {action_name}")
        
        if action_name == "create_goal_task" or action_name == "create_task":
            success, msg, _ = await ActionConfirmationService.process_task_creation_with_verification(
                db, user_id, payload
            )
            return success, msg
        else:
            return False, f"Unsupported action '{action_name}'"
        
