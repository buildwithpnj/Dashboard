from typing import Dict, Any
from app.repositories.preview_trace_events import PreviewTraceEventsRepository

class PreviewMetrics:
    @classmethod
    def get_aggregated_metrics(cls) -> Dict[str, Any]:
        traces = PreviewTraceEventsRepository.get_all_traces()
        total = len(traces)
        if total == 0:
            return {"total_requests": 0, "avg_latency_ms": 0.0, "timeout_rate": 0.0}

        latencies = [t["latency_ms"] for t in traces]
        model_latencies = [t["model_latency_ms"] for t in traces if t["model_latency_ms"] > 0]
        timeouts = sum(1 for t in traces if t["is_timeout"])
        blocked = sum(1 for t in traces if t["status"] == "blocked")
        
        # Calculate session abandonment points: count of sessions that reached exactly 1 turn, 2 turns, etc.
        session_turns: Dict[str, int] = {}
        for t in traces:
            session_turns[t["session_id"]] = session_turns.get(t["session_id"], 0) + 1
            
        abandonment_distribution: Dict[int, int] = {}
        for turns in session_turns.values():
            abandonment_distribution[turns] = abandonment_distribution.get(turns, 0) + 1

        return {
            "total_requests": total,
            "average_latency_ms": round(sum(latencies) / total, 2),
            "average_model_latency_ms": round(sum(model_latencies) / len(model_latencies), 2) if model_latencies else 0.0,
            "blocked_count": blocked,
            "timeout_frequency": timeouts,
            "timeout_rate_percentage": round((timeouts / total) * 100.0, 2),
            "session_abandonment_distribution": abandonment_distribution
        }
