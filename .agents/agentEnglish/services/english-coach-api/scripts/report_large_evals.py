import argparse
import asyncio
import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("report_large_evals")

# Ensure app is on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.repositories.batch_eval_runs import BatchEvalRunsRepository
from app.repositories.eval_examples import EvalExamplesRepository
from app.repositories.error_clusters import ErrorClustersRepository

async def generate_report(args):
    async with AsyncSessionLocal() as db:

        runs_repo = BatchEvalRunsRepository(db)
        eval_examples_repo = EvalExamplesRepository(db)
        error_clusters_repo = ErrorClustersRepository(db)

        run_id = args.run_id
        if not run_id:
            recent_runs = await runs_repo.list_runs(limit=1)
            if not recent_runs:
                logger.error("No eval runs found. Cannot generate report.")
                return
            run_id = recent_runs[0].id

        run = await runs_repo.get_by_id(run_id)
        if not run:
            logger.error(f"Run {run_id} not found.")
            return

        examples = await eval_examples_repo.get_by_run(run_id, limit=1000)
        errors = await error_clusters_repo.get_aggregated(run_id)

        # Calculate metrics
        total = len(examples)
        passed = sum(1 for ex in examples if ex.composite_score >= 0.5)
        failed = total - passed
        pass_rate = (passed / total * 100.0) if total > 0 else 0.0

        avg_score = (sum(ex.composite_score for ex in examples) / total) if total > 0 else 0.0
        total_cost = run.cost_usd
        cost_per_100 = (total_cost / total * 100.0) if total > 0 else 0.0

        # Output visual layout
        print("=" * 80)
        print(f"                      LARGE-SCALE EVALUATION RUN REPORT                      ")
        print("=" * 80)
        print(f"Run ID:             {run.id}")
        print(f"Dataset Name:       {run.dataset_name:<30} Product ID:       {run.product_id}")
        print(f"Model Name:         {run.model_name:<30} Status:           {run.status}")
        print(f"Started At:         {run.started_at} completed:        {run.completed_at}")
        print("-" * 80)
        print(f"Total Examples:     {total:<30} Avg Score:       {avg_score:.4f}")
        print(f"Passed Examples:    {passed:<30} Failed:           {failed}")
        print(f"Pass Rate:          {pass_rate:.2f}%")
        print(f"Total Cost (USD):   ${total_cost:<23.6f} Cost/100 Items:   ${cost_per_100:.6f}")

        print("-" * 80)
        
        # Display failure buckets
        if errors:
            print("Failure Bucket Distribution:")
            print(f"  {'Error Category':<30} | {'Count':<5}")
            print("  " + "-" * 38)
            for err in errors:
                print(f"  {err['bucket_name']:<30} | {err['count']:<5}")
        else:
            print("No failure clusters logged for this run.")
            
        print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print formatted metrics summary report for evaluation runs.")
    parser.add_argument("--run-id", type=str, help="ID of the evaluation run. Defaults to latest.")
    args = parser.parse_args()
    asyncio.run(generate_report(args))
