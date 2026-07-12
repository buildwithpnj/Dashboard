from .public_response_checker import PublicResponseChecker
from typing import Dict, Any, List

class PreviewQualityMonitor:
    _scores: List[float] = []
    _failures: List[Dict[str, Any]] = []

    @classmethod
    def monitor_response(cls, session_id: str, prompt: str, response: str) -> float:
        is_valid = PublicResponseChecker.check_response(response)
        score = 1.0 if is_valid else 0.0
        cls._scores.append(score)
        
        if not is_valid:
            cls._failures.append({
                "session_id": session_id,
                "prompt": prompt,
                "response": response,
                "reason": "failed_safety_or_quality_checks"
            })
            
        return score

    @classmethod
    def get_quality_stats(cls) -> Dict[str, Any]:
        total = len(cls._scores)
        if total == 0:
            return {"pass_rate": 100.0, "total_runs": 0, "failure_count": 0}
            
        pass_count = sum(cls._scores)
        pass_rate = (pass_count / total) * 100.0
        return {
            "pass_rate_percentage": round(pass_rate, 2),
            "total_runs": total,
            "failure_count": len(cls._failures)
        }

    @classmethod
    def get_failures(cls) -> List[Dict[str, Any]]:
        return cls._failures
