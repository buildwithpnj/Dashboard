import logging
from typing import Dict, Any, Callable, Awaitable

logger = logging.getLogger("self_healing_retry")

class SelfHealingRetryService:
    @classmethod
    async def run_with_self_healing_retry(
        cls,
        operation: Callable[[], Awaitable[Any]],
        max_attempts: int = 3
    ) -> Any:
        """
        Runs operation, retrying on transient errors.
        """
        attempts = 0
        while attempts < max_attempts:
            try:
                attempts += 1
                return await operation()
            except Exception as e:
                err_msg = str(e).lower()
                is_transient = "timeout" in err_msg or "network" in err_msg or "connection" in err_msg
                
                if is_transient and attempts < max_attempts:
                    logger.warning(f"Transient error detected: '{e}'. Triggering self-healing retry attempt {attempts + 1}...")
                else:
                    logger.error(f"Operation failed permanently on attempt {attempts}: {e}")
                    raise e
