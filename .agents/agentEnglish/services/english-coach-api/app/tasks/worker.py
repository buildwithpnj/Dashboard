import logging
import concurrent.futures
from typing import Callable, Any

logger = logging.getLogger(__name__)

class BackgroundJobWorker:
    """In-memory background execution queue using a ThreadPoolExecutor."""
    
    # Restrict to 3 worker threads locally to prevent memory spikes
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=3, thread_name_prefix="warborn-worker")

    @classmethod
    def submit_job(cls, task_func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Queues a job for async thread execution."""
        try:
            cls._executor.submit(task_func, *args, **kwargs)
            logger.info(f"Submitted background job: {task_func.__name__}")
        except Exception as e:
            logger.error(f"Failed to submit background task {task_func.__name__}: {e}")
            
    @classmethod
    def shutdown(cls) -> None:
        """Gracefully terminates background thread workers pool."""
        cls._executor.shutdown(wait=False)
