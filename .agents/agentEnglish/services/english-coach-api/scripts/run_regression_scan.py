import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta

# Ensure app is on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.db.models import LiveQualityMetric
from app.repositories.live_quality_metrics import LiveQualityMetricsRepository
from app.repositories.regression_events import RegressionEventsRepository
from app.services.baseline_comparator import BaselineComparator
from app.services.regression_detector import RegressionDetector

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("regression_scan")

async def run_scan(args):
    async with AsyncSessionLocal() as db:
        metrics_repo = LiveQualityMetricsRepository(db)
        regression_repo = RegressionEventsRepository(db)
        comparator = BaselineComparator()
        detector = RegressionDetector(regression_repo, comparator)

        # 1. Fetch latest metric
        history = await metrics_repo.list_history(args.tenant_id, args.product_id, limit=2)
        if not history:
            logger.info("No rolling metrics found to scan. Seeding baseline and regressed metrics.")
            baseline = LiveQualityMetric(
                tenant_id=args.tenant_id,
                product_id=args.product_id,
                model_name="mock",
                prompt_version="v9.0",
                window_size="24h",
                avg_score=0.90,
                pass_rate=0.95,
                escalation_rate=0.01,
                review_queue_rate=0.04,
                budget_spend=0.45,
                token_usage=2000
            )
            current = LiveQualityMetric(
                tenant_id=args.tenant_id,
                product_id=args.product_id,
                model_name="mock",
                prompt_version="v9.1",
                window_size="24h",
                avg_score=0.78, # Drop of >10% (critical)
                pass_rate=0.82, # Drop of >5%
                escalation_rate=0.05, # Increase of >2%
                review_queue_rate=0.15,
                budget_spend=0.60, # Increase of >20%
                token_usage=2900
            )
            await metrics_repo.create(baseline)
            await metrics_repo.create(current)
            await db.commit()
            history = [current, baseline]

        current = history[0]
        baseline = history[1] if len(history) > 1 else history[0]

        logger.info(f"Scanning for regressions between current ({current.prompt_version}) and baseline ({baseline.prompt_version})")
        events = await detector.detect_regressions(
            current=current,
            baseline=baseline,
            tenant_id=args.tenant_id,
            product_id=args.product_id
        )

        await db.commit()

        print("\n" + "=" * 80)
        print("                         REGRESSION SCAN RESULTS                          ")
        print("=" * 80)
        print(f"Product: {args.product_id:<20} Tenant: {args.tenant_id:<20}")
        print("-" * 80)
        if not events:
            print("No quality regressions detected. System is stable.")
        else:
            print(f"ALERT: {len(events)} regression event(s) logged!")
            for event in events:
                print(f"  * [{event.severity.upper()}] Metric '{event.metric_name}' regressed from {event.baseline_value:.4f} to {event.current_value:.4f}")
        print("=" * 80 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for quality and budget regressions.")
    parser.add_argument("--product-id", type=str, default="english_coach")
    parser.add_argument("--tenant-id", type=str, default="default_tenant")
    args = parser.parse_args()
    asyncio.run(run_scan(args))
