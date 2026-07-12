from app.db.models import LiveQualityMetric
from app.services.model_mix_planner import ModelMixPlanner
from app.services.cost_quality_optimizer import CostQualityOptimizer

def test_model_mix_planner():
    planner = ModelMixPlanner()

    # 1. Budget breach target mix
    plan_budget = planner.recommend_model_mix(total_count=100, failure_rate=0.05, budget_utilization_pct=95.0)
    assert plan_budget["cheap_pct"] == 85
    assert plan_budget["premium_pct"] == 5

    # 2. Quality drop mix
    plan_quality = planner.recommend_model_mix(total_count=100, failure_rate=0.25, budget_utilization_pct=50.0)
    assert plan_quality["premium_pct"] == 30

    # 3. Balanced mix
    plan_default = planner.recommend_model_mix(total_count=100, failure_rate=0.05, budget_utilization_pct=40.0)
    assert plan_default["cheap_pct"] == 60

def test_cost_quality_optimizer():
    planner = ModelMixPlanner()
    optimizer = CostQualityOptimizer(planner)

    metric = LiveQualityMetric(
        avg_score=0.89,
        pass_rate=0.90,
        budget_spend=1.50,
        token_usage=3000
    )

    result = optimizer.optimize(metric)
    assert result["cost_per_passed"] > 0.0
    assert "suggested_mix" in result
