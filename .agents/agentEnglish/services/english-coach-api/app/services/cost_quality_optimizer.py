from app.db.models import LiveQualityMetric
from app.services.model_mix_planner import ModelMixPlanner

class CostQualityOptimizer:
    """Service to optimize cost vs. quality by evaluating live metrics and recommending routing adjustments."""

    def __init__(self, mix_planner: ModelMixPlanner):
        self.mix_planner = mix_planner

    def optimize(self, metrics: LiveQualityMetric) -> dict:
        """Calculates cost metrics, checks for model downgrade recommendations, and plans the model mix."""
        # Standardize pass rate to fraction and percentage
        pass_rate = metrics.pass_rate if metrics.pass_rate <= 1.0 else metrics.pass_rate / 100.0
        pass_rate_pct = pass_rate * 100.0
        failure_rate_pct = 100.0 - pass_rate_pct

        # Estimate example counts (defaulting to safe values if not present dynamically)
        total_count = getattr(metrics, "total_count", 100)
        if total_count <= 0:
            total_count = 1

        passed_count = total_count * pass_rate
        if passed_count <= 0:
            passed_count = 0.001  # Prevent division by zero

        # Cost per passed example
        cost_per_passed = metrics.budget_spend / passed_count

        # Cost per gold promotion (assume ~10% of total examples are promoted to gold if not defined)
        gold_promotions = getattr(metrics, "gold_promotions", max(1, int(total_count * 0.1)))
        if gold_promotions <= 0:
            gold_promotions = 1
        cost_per_gold_promotion = metrics.budget_spend / gold_promotions

        # Evaluate model switch condition:
        # If pass rate is high (>85%) but premium model is highly used and cost is high, recommend downgrade to standard.
        model_name = metrics.model_name.lower() if metrics.model_name else ""
        is_premium_used = "premium" in model_name or "gpt-4" in model_name or "gpt-4o" in model_name
        cost_high = metrics.budget_spend > 5.0  # Set standard threshold for high spend in evaluation window

        action_recommendation = "maintain"
        if pass_rate_pct > 85.0 and is_premium_used and cost_high:
            action_recommendation = "downgrade to standard"

        # Recommends model mix targets using mix_planner
        budget_limit = getattr(metrics, "budget_limit", 10.0)
        budget_utilization_pct = (metrics.budget_spend / budget_limit) * 100.0 if budget_limit > 0 else 0.0

        suggested_mix = self.mix_planner.recommend_model_mix(
            total_count=total_count,
            failure_rate=failure_rate_pct,
            budget_utilization_pct=budget_utilization_pct
        )

        return {
            "cost_per_passed": float(cost_per_passed),
            "cost_per_gold_promotion": float(cost_per_gold_promotion),
            "action_recommendation": action_recommendation,
            "suggested_mix": suggested_mix
        }
