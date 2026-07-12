from typing import List, Dict, Any

class PreviewTraceEventsRepository:
    _traces: List[Dict[str, Any]] = []

    @classmethod
    def log_trace(cls, trace: Dict[str, Any]):
        cls._traces.append(trace)

    @classmethod
    def get_all_traces(cls) -> List[Dict[str, Any]]:
        return cls._traces
