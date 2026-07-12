import argparse
import asyncio
import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("report_cost_quality")

# Ensure app is on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.db.models import LiveQualityMetric
from app.repositories.live_quality_metrics import LiveQualityMetricsRepository
from app.services.model_mix_planner import ModelMixPlanner
from app.services.cost_quality_optimizer import CostQualityOptimizer

async def run_report(args):
    async with AsyncSessionLocal() as db:
        metrics_repo = LiveQualityMetricsRepository(db)
        
        # 1. Fetch latest rolling metrics
        history = await metrics_repo.list_history(args.tenant_id, args.product_id, limit=1)
        if not history:
            logger.info("No metrics found to optimize. Seeding mock metric.")
            metric = LiveQualityMetric(
                id="mock-opt-metric-id",
                tenant_id=args.tenant_id,
                product_id=args.product_id,
                model_name="mock",
                prompt_version="v9.0",
                window_size="24h",
                avg_score=0.82,
                pass_rate=0.86,
                escalation_rate=0.01,
                review_queue_rate=0.05,
                budget_spend=1.20, # Higher spend triggers optimizer warnings
                token_usage=3200
            )
            await metrics_repo.create(metric)
            await db.commit()
            history = [metric]

        current_metric = history[0]

        # 2. Run Optimizer
        mix_planner = ModelMixPlanner()
        optimizer = CostQualityOptimizer(mix_planner)
        
        opt_report = optimizer.optimize(current_metric)
        mix = opt_report["suggested_mix"]

        print("\n" + "=" * 80)
        print(f"                      COST & QUALITY OPTIMIZATION REPORT                      ")
        print("=" * 80)
        print(f"Product: {args.product_id:<20} Tenant: {args.tenant_id:<20}")
        print("-" * 80)
        print(f"Estimated Cost Per Passed Example:  ${opt_report['cost_per_passed']:.6f}")
        print(f"Action Recommendation:              {opt_report['action_recommendation']}")
        print("-" * 80)
        print(f"Suggested Allocation Model Mix Plan:")
        print(f"  * Cheap Model Tier:     {mix['cheap_pct']}%")
        print(f"  * Standard Model Tier:  {mix['standard_pct']}%")
        print(f"  * Premium Model Tier:   {mix['premium_pct']}%")
        print(f"  * Rationale:            {mix['reason']}")
        print("=" * 80 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cost/quality model mix optimization reports.")
    parser.add_argument("--product-id", type=str, default="english_coach")
    parser.add_argument("--tenant-id", type=str, default="default_tenant")
    
    args = parser.parse_args()
    asyncio.run(run_report(args))
