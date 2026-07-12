import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RequestTraceSpan:
    """Decoupled trace span logger mapping trace IDs across process nodes."""

    def __init__(self, span_name: str, trace_id: Optional[str] = None):
        self.span_name = span_name
        self.trace_id = trace_id or str(uuid.uuid4())

    def __enter__(self):
        logger.info(f"[TRACE START] Node: '{self.span_name}' | TraceID: {self.trace_id}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"[TRACE ERROR] Node: '{self.span_name}' | TraceID: {self.trace_id} | Exception: {exc_val}")
        else:
            logger.info(f"[TRACE SUCCESS] Node: '{self.span_name}' | TraceID: {self.trace_id}")
        return False
