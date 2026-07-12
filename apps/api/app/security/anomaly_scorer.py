import time
from typing import Dict, List

class AnomalyScorer:
    # Track IP/Session request timestamps
    _timestamps: Dict[str, List[float]] = {}

    @classmethod
    def score_request(cls, session_id: str) -> float:
        """Returns anomaly score between 0.0 (normal) and 1.0 (highly anomalous)."""
        current_time = time.time()
        if session_id not in cls._timestamps:
            cls._timestamps[session_id] = [current_time]
            return 0.0

        history = cls._timestamps[session_id]
        history.append(current_time)
        
        # Keep only last 5 requests
        if len(history) > 5:
            history.pop(0)

        if len(history) < 2:
            return 0.0

        # Calculate time differences between requests
        intervals = [history[i] - history[i-1] for i in range(1, len(history))]
        avg_interval = sum(intervals) / len(intervals)

        # If average request interval is less than 1.5 seconds, flag as bot anomaly
        if avg_interval < 1.5:
            return 1.0
        elif avg_interval < 3.0:
            return 0.5
        return 0.0
