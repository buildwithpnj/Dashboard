class ModelMixPlanner:
    """Service to recommend optimal allocation of cheap, standard, and premium models."""

    def recommend_model_mix(
        self, total_count: int, failure_rate: float, budget_utilization_pct: float
    ) -> dict:
        """Recommends percentage targets for model mix based on count, failure rate, and budget usage."""
        # Handle both percentage (e.g. 95.0) and decimal ratio (e.g. 0.95) formats
        b_util = budget_utilization_pct * 100.0 if 0.0 <= budget_utilization_pct <= 1.0 else budget_utilization_pct
        f_rate = failure_rate * 100.0 if 0.0 <= failure_rate <= 1.0 else failure_rate

        if b_util > 90.0:
            return {
                "cheap_pct": 85,
                "standard_pct": 10,
                "premium_pct": 5,
                "reason": "Budget utilization is high (>90%), prioritizing cost reduction."
            }
        elif f_rate > 20.0 and b_util < 70.0:
            return {
                "cheap_pct": 30,
                "standard_pct": 40,
                "premium_pct": 30,
                "reason": "Failure rate is high (>20%) and budget room exists (<70%), shifting to premium/standard models."
            }
        else:
            return {
                "cheap_pct": 60,
                "standard_pct": 35,
                "premium_pct": 5,
                "reason": "Standard balanced operation."
            }
