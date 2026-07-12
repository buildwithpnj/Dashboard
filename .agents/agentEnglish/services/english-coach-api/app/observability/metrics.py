import time
from typing import Dict, Any, List

class ObservabilityMetricsTracker:
    """Aggregates execution metrics, token spends, and cache performance details."""
    
    # Static dictionary storage to persist across requests (since in-memory is requested for V1)
    _metrics = {
        "total_requests": 0,
        "total_latency_ms": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cached_tokens": 0,
        "total_cost_usd": 0.0,
        "ambiguity_counts": 0,
        "feedback_total": 0,
        "feedback_approved": 0,
        "auth_denied_counts": 0,
        "token_budget_drops": 0,
        "background_jobs_run": 0,
        "product_splits": {
            "english_coach": 0,
            "lifeos_coach": 0,
            "family_checkin": 0
        }
    }

    @classmethod
    def record_request(
        cls,
        product_id: str,
        latency_ms: float,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        cost_usd: float,
        is_ambiguous: bool
    ) -> None:
        """Records metadata metrics from a completed agent transaction."""
        cls._metrics["total_requests"] += 1
        cls._metrics["total_latency_ms"] += latency_ms
        cls._metrics["total_input_tokens"] += input_tokens
        cls._metrics["total_output_tokens"] += output_tokens
        cls._metrics["total_cached_tokens"] += cached_tokens
        cls._metrics["total_cost_usd"] += cost_usd
        if is_ambiguous:
            cls._metrics["ambiguity_counts"] += 1

        cls._metrics["product_splits"][product_id] = cls._metrics["product_splits"].get(product_id, 0) + 1

    @classmethod
    def record_feedback(cls, approved: bool) -> None:
        """Records feedback responses."""
        cls._metrics["feedback_total"] += 1
        if approved:
            cls._metrics["feedback_approved"] += 1

    @classmethod
    def record_auth_denied(cls) -> None:
        """Logs access denial occurrences."""
        cls._metrics["auth_denied_counts"] += 1

    @classmethod
    def record_budget_drop(cls) -> None:
        """Logs dynamic exemplar context truncation drops."""
        cls._metrics["token_budget_drops"] += 1

    @classmethod
    def record_background_job(cls) -> None:
        """Logs background task submissions."""
        cls._metrics["background_jobs_run"] += 1

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        """Generates the aggregated stats summary for admin endpoints."""
        total = cls._metrics["total_requests"] or 1
        fb_total = cls._metrics["feedback_total"] or 1
        
        return {
            "total_requests": cls._metrics["total_requests"],
            "average_latency_ms": cls._metrics["total_latency_ms"] / total,
            "total_input_tokens": cls._metrics["total_input_tokens"],
            "total_output_tokens": cls._metrics["total_output_tokens"],
            "total_cached_tokens": cls._metrics["total_cached_tokens"],
            "total_cost_usd": cls._metrics["total_cost_usd"],
            "ambiguity_rate": cls._metrics["ambiguity_counts"] / total,
            "feedback_approval_rate": cls._metrics["feedback_approved"] / fb_total,
            "auth_denied_counts": cls._metrics["auth_denied_counts"],
            "token_budget_drops": cls._metrics["token_budget_drops"],
            "background_jobs_run": cls._metrics["background_jobs_run"],
            "product_usage_splits": cls._metrics["product_splits"]
        }
