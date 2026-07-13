from typing import Dict, Any, List

class AgentAnalyticsService:
    _latency_records: List[float] = []

    @classmethod
    def record_latency(cls, ms: float) -> None:
        """
        Appends runtime latency record in ms.
        """
        cls._latency_records.append(ms)

    @classmethod
    def get_average_latency(cls) -> float:
        """
        Returns average latency of agent execution.
        """
        if not cls._latency_records:
            return 0.0
        return sum(cls._latency_records) / len(cls._latency_records)

    @classmethod
    def detect_latency_spike(cls, threshold_ms: float = 2000.0) -> bool:
        """
        Returns true if the latest latency is higher than the threshold.
        """
        if not cls._latency_records:
            return False
        return cls._latency_records[-1] > threshold_ms
