import time
import uuid
import logging
from typing import Optional, Any, Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class ExecutionSpan:
    """Represents a single trace execution span tracking latencies and cost attributes."""
    
    def __init__(self, name: str, trace_id: str, parent_span_id: Optional[str] = None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = str(uuid.uuid4())[:8]
        self.parent_span_id = parent_span_id
        self.start_time = 0.0
        self.duration_ms = 0.0

    def start(self) -> None:
        self.start_time = time.perf_counter()
        logger.info(
            f"[SPAN START] name={self.name} trace_id={self.trace_id} "
            f"span_id={self.span_id} parent_span_id={self.parent_span_id}"
        )

    def finish(self, status: str = "success", metadata: Optional[Dict[str, Any]] = None) -> None:
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000.0
        meta_str = f" metadata={metadata}" if metadata else ""
        logger.info(
            f"[SPAN END] name={self.name} trace_id={self.trace_id} "
            f"span_id={self.span_id} duration_ms={self.duration_ms:.2f}ms "
            f"status={status}{meta_str}"
        )

class PlatformTracer:
    """Manages active tracing scopes and parent context states."""
    
    @classmethod
    @contextmanager
    def span(cls, name: str, trace_id: Optional[str] = None, parent_span_id: Optional[str] = None):
        tid = trace_id or str(uuid.uuid4())
        span_obj = ExecutionSpan(name, tid, parent_span_id)
        span_obj.start()
        try:
            yield span_obj
            span_obj.finish("success")
        except Exception as e:
            span_obj.finish("error", {"error": str(e)})
            raise e
