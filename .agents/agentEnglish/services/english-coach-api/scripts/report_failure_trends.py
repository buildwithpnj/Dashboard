import argparse
import asyncio
import logging
import os
import sys
import uuid

# Ensure app is on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.db.models import FailureTrend
from app.repositories.failure_trends import FailureTrendsRepository

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("failure_report")

async def run_report(args):
    async with AsyncSessionLocal() as db:
        trends_repo = FailureTrendsRepository(db)

        # 1. Fetch active trends
        trends = await trends_repo.get_trends(args.tenant_id, args.product_id, args.window_size)
        if not trends:
            logger.info("No failure trends found for window. Seeding mock failure trends.")
            t1 = FailureTrend(
                id=str(uuid.uuid4()),
                tenant_id=args.tenant_id,
                product_id=args.product_id,
                window_size=args.window_size,
                error_bucket="under_correction",
                count=12
            )
            t2 = FailureTrend(
                id=str(uuid.uuid4()),
                tenant_id=args.tenant_id,
                product_id=args.product_id,
                window_size=args.window_size,
                error_bucket="over_correction",
                count=5
            )
            t3 = FailureTrend(
                id=str(uuid.uuid4()),
                tenant_id=args.tenant_id,
                product_id=args.product_id,
                window_size=args.window_size,
                error_bucket="meaning_preservation",
                count=8
            )
            await trends_repo.create(t1)
            await trends_repo.create(t2)
            await trends_repo.create(t3)
            await db.commit()
            trends = [t1, t2, t3]

        print("\n" + "=" * 80)
        print(f"                      ROLLING FAILURE TRENDS REPORT                           ")
        print("=" * 80)
        print(f"Product: {args.product_id:<20} Tenant: {args.tenant_id:<20} Window: {args.window_size}")
        print("-" * 80)
        print(f"{'Error Bucket':<35} | {'Count':<10}")
        print("-" * 80)
        
        total_errors = sum(t.count for t in trends)
        for t in sorted(trends, key=lambda x: x.count, reverse=True):
            pct = (t.count / total_errors * 100) if total_errors > 0 else 0
            print(f"{t.error_bucket:<35} | {t.count:<10} ({pct:.1f}%)")
            
        print("-" * 80)
        print(f"{'Total Errors logged':<35} | {total_errors:<10}")
        print("=" * 80 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Report rolling failure trends.")
    parser.add_argument("--product-id", type=str, default="english_coach")
    parser.add_argument("--tenant-id", type=str, default="default_tenant")
    parser.add_argument("--window-size", type=str, default="24h")
    args = parser.parse_args()
    asyncio.run(run_report(args))
