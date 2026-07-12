import argparse
import asyncio
import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("promote_gold_examples")

# Ensure app is on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.repositories.gold_examples import GoldExamplesRepository
from app.repositories.hard_negative_examples import HardNegativeExamplesRepository
from app.repositories.eval_examples import EvalExamplesRepository
from app.repositories.batch_eval_runs import BatchEvalRunsRepository
from app.services.gold_dataset_service import GoldDatasetService

async def promote_examples(args):
    async with AsyncSessionLocal() as db:

        runs_repo = BatchEvalRunsRepository(db)
        eval_examples_repo = EvalExamplesRepository(db)
        gold_repo = GoldExamplesRepository(db)
        hard_neg_repo = HardNegativeExamplesRepository(db)
        
        gold_service = GoldDatasetService(gold_repo, hard_neg_repo, eval_examples_repo)

        run_id = args.run_id
        if not run_id:
            # Look up the latest completed run
            recent_runs = await runs_repo.list_runs(limit=1)
            if not recent_runs:
                logger.error("No eval runs found. Please run an evaluation script first.")
                return
            run_id = recent_runs[0].id
            logger.info(f"Using latest evaluation run ID: {run_id}")

        run = await runs_repo.get_by_id(run_id)
        if not run:
            logger.error(f"Eval run with ID {run_id} not found.")
            return

        # Perform the promotion loop
        summary = await gold_service.promote_from_run(
            run_id=run_id,
            dataset_name=run.dataset_name,
            product_id=run.product_id,
            gold_threshold=args.threshold,
            hard_neg_threshold=args.hard_neg_threshold,
            require_review=args.require_review
        )

        logger.info(f"Promotion workflow complete. Promoted {summary['gold_promoted']} examples to Gold dataset, and {summary['hard_negatives_created']} to Hard Negatives.")
        print(f"\nSuccessfully promoted {summary['gold_promoted']} gold items and {summary['hard_negatives_created']} hard negatives from run {run_id}.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Promote high-quality model outputs to Gold dataset.")
    parser.add_argument("--run-id", type=str, help="ID of the evaluation run to promote from. Defaults to latest.")
    parser.add_argument("--threshold", type=float, default=settings.GOLD_PROMOTION_THRESHOLD, help="Composite score quality threshold.")
    parser.add_argument("--hard-neg-threshold", type=float, default=0.4, help="Composite score threshold for hard negatives.")
    parser.add_argument("--require-review", action="store_true", default=True, help="Require human operator validation (PENDING status).")
    
    args = parser.parse_args()
    asyncio.run(promote_examples(args))
