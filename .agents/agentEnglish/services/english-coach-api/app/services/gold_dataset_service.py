import uuid
import logging
from typing import List, Optional

from app.core.config import settings
from app.db.models import GoldExample, HardNegativeExample, EvalExampleResult
from app.repositories.gold_examples import GoldExamplesRepository
from app.repositories.hard_negative_examples import HardNegativeExamplesRepository
from app.repositories.eval_examples import EvalExamplesRepository

logger = logging.getLogger(__name__)


class GoldDatasetService:
    """Manages quality-gated promotion of eval results into gold and hard-negative datasets.
    
    Promotion rules:
    - Only promotes examples that pass quality threshold (default 0.85 composite score)
    - Requires provenance tracking (source dataset, run ID, example hash)
    - Creates separate gold, hard-negative, and ambiguous-case partitions
    - Versions every promoted example
    """

    def __init__(
        self,
        gold_repo: GoldExamplesRepository,
        hard_neg_repo: HardNegativeExamplesRepository,
        eval_examples_repo: EvalExamplesRepository,
    ):
        self.gold_repo = gold_repo
        self.hard_neg_repo = hard_neg_repo
        self.eval_examples_repo = eval_examples_repo

    async def promote_from_run(
        self,
        run_id: str,
        dataset_name: str,
        product_id: str,
        gold_threshold: Optional[float] = None,
        hard_neg_threshold: float = 0.4,
        tenant_id: str = "default_tenant",
        promotion_version: str = "v1.0",
        require_review: bool = True,
    ) -> dict:
        """Promotes high-scoring examples to gold and low-scoring to hard-negatives.
        
        Args:
            run_id: The batch eval run to promote from.
            dataset_name: Source dataset name for provenance.
            product_id: Target product for the promoted examples.
            gold_threshold: Min composite score for gold promotion.
            hard_neg_threshold: Max composite score for hard-negative classification.
            tenant_id: Tenant scope.
            promotion_version: Version tag for promoted examples.
            require_review: If True, gold examples start as PENDING review.
            
        Returns:
            Summary dict with promotion counts.
        """
        threshold = gold_threshold or settings.GOLD_PROMOTION_THRESHOLD

        # Get promotable examples
        promotable = await self.eval_examples_repo.get_promotable(run_id, threshold=threshold)
        hard_negatives = await self.eval_examples_repo.get_hard_negatives(run_id, threshold=hard_neg_threshold)

        gold_created = 0
        neg_created = 0

        # Promote gold examples
        for ex in promotable:
            gold = GoldExample(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                product_id=product_id,
                task_type=ex.task_type,
                input_text=ex.input_text,
                output_text=ex.model_output or "",
                composite_score=ex.composite_score,
                source_dataset=dataset_name,
                source_example_hash=ex.example_hash,
                source_run_id=run_id,
                promotion_version=promotion_version,
                review_status="PENDING" if require_review else "APPROVED",
            )
            await self.gold_repo.create(gold)

            # Mark the eval example as promoted
            ex.status = "PROMOTED"
            gold_created += 1

        # Create hard-negative examples
        for ex in hard_negatives:
            neg = HardNegativeExample(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                product_id=product_id,
                task_type=ex.task_type,
                input_text=ex.input_text,
                bad_output=ex.model_output or "",
                error_bucket=ex.error_bucket or "unknown",
                composite_score=ex.composite_score,
                source_dataset=dataset_name,
                source_example_hash=ex.example_hash,
                source_run_id=run_id,
            )
            await self.hard_neg_repo.create(neg)

            ex.status = "REJECTED"
            neg_created += 1

        await self.gold_repo.db.commit()

        summary = {
            "run_id": run_id,
            "gold_promoted": gold_created,
            "hard_negatives_created": neg_created,
            "gold_threshold": threshold,
            "hard_neg_threshold": hard_neg_threshold,
            "require_review": require_review,
            "promotion_version": promotion_version,
        }
        logger.info(f"Promotion complete for run {run_id}: {gold_created} gold, {neg_created} hard-negatives")
        return summary

    async def get_promotion_stats(self, tenant_id: str = "default_tenant") -> dict:
        """Returns aggregate promotion statistics for a tenant."""
        gold_counts = await self.gold_repo.count_by_status(tenant_id)
        neg_counts = await self.hard_neg_repo.count_by_bucket(tenant_id)

        return {
            "gold_examples": gold_counts,
            "hard_negatives_by_bucket": neg_counts,
            "total_gold": sum(gold_counts.values()),
            "total_hard_negatives": sum(neg_counts.values()),
        }
