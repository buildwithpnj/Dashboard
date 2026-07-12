import logging
from typing import Dict, Any, Callable, Awaitable
from app.services.critic_service import CriticService

logger = logging.getLogger(__name__)

class QualityGate:
    """Interviews generated payloads, running exactly one repair loop on validation issues."""

    def __init__(self, critic: CriticService):
        self.critic = critic

    async def validate_and_repair(
        self,
        user_input: str,
        response_data: Dict[str, Any],
        repair_fn: Callable[[], Awaitable[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Runs critic evaluations, executing the repair callback on errors to secure performance levels."""
        eval_res = await self.critic.evaluate_output(user_input, response_data)
        if eval_res["is_valid"]:
            return response_data

        logger.warning(f"Quality gate validation issues detected: {eval_res['issues']}. Triggering repair pass.")
        try:
            # Trigger the single execution repair pass callable
            repaired_data = await repair_fn()
            
            # Re-evaluate repaired output
            second_eval = await self.critic.evaluate_output(user_input, repaired_data)
            if second_eval["is_valid"]:
                logger.info("Quality gate successfully repaired the response payload.")
                return repaired_data
                
            logger.warning(f"Quality gate second evaluation failed: {second_eval['issues']}. Falling back to default.")
            return repaired_data
        except Exception as err:
            logger.error(f"Exception encountered during quality gate repair execution: {err}")
            
        return response_data
