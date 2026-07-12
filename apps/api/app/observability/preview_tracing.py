import time
from typing import Dict, Any, Optional
from app.repositories.preview_trace_events import PreviewTraceEventsRepository

class PreviewTracing:
    @classmethod
    def start_trace(cls, session_id: str, prompt: str) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "prompt": prompt,
            "start_time": time.perf_counter(),
            "model_start_time": None,
            "model_end_time": None,
            "end_time": None,
            "latency_ms": 0.0,
            "model_latency_ms": 0.0,
            "tokens_used": 0,
            "cost_usd": 0.0,
            "blocked_reason": None,
            "allowed_intent": None,
            "is_timeout": False
        }

    @classmethod
    def record_model_start(cls, trace: Dict[str, Any]):
        trace["model_start_time"] = time.perf_counter()

    @classmethod
    def record_model_end(cls, trace: Dict[str, Any], tokens: int, cost: float):
        trace["model_end_time"] = time.perf_counter()
        trace["tokens_used"] = tokens
        trace["cost_usd"] = cost
        if trace["model_start_time"]:
            trace["model_latency_ms"] = (trace["model_end_time"] - trace["model_start_time"]) * 1000.0

    @classmethod
    def end_trace(
        cls, 
        trace: Dict[str, Any], 
        status: str, 
        blocked_reason: Optional[str] = None, 
        intent: Optional[str] = None,
        is_timeout: bool = False
    ):
        trace["end_time"] = time.perf_counter()
        trace["latency_ms"] = (trace["end_time"] - trace["start_time"]) * 1000.0
        trace["status"] = status
        trace["blocked_reason"] = blocked_reason
        trace["allowed_intent"] = intent
        trace["is_timeout"] = is_timeout
        
        # Log to repository
        PreviewTraceEventsRepository.log_trace(trace)
