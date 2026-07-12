import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models import EvalExampleResult
from app.repositories.gold_examples import GoldExamplesRepository
from app.repositories.hard_negative_examples import HardNegativeExamplesRepository
from app.repositories.eval_examples import EvalExamplesRepository
from app.services.gold_dataset_service import GoldDatasetService

@pytest.mark.anyio
async def test_gold_dataset_promotion():
    async with AsyncSessionLocal() as session:
        gold_repo = GoldExamplesRepository(session)
        hard_neg_repo = HardNegativeExamplesRepository(session)
        eval_examples_repo = EvalExamplesRepository(session)
        service = GoldDatasetService(gold_repo, hard_neg_repo, eval_examples_repo)

        run_id = f"run-{uuid.uuid4()}"

        # 1. Add sample evaluation results
        ex_gold = EvalExampleResult(
            id=str(uuid.uuid4()),
            run_id=run_id,
            example_hash="hash1",
            task_type="correction",
            input_text="He go.",
            model_output="He went.",
            composite_score=0.90,
            status="SCORED"
        )
        ex_neg = EvalExampleResult(
            id=str(uuid.uuid4()),
            run_id=run_id,
            example_hash="hash2",
            task_type="correction",
            input_text="I has.",
            model_output="I has.",
            composite_score=0.30,
            status="SCORED",
            error_bucket="under_correction"
        )
        await eval_examples_repo.create(ex_gold)
        await eval_examples_repo.create(ex_neg)
        await session.flush()

        tenant_id = f"tenant-{uuid.uuid4()}"

        # 2. Promote run outputs
        summary = await service.promote_from_run(
            run_id=run_id,
            dataset_name="test_dataset",
            product_id="english_coach",
            gold_threshold=0.85,
            hard_neg_threshold=0.40,
            tenant_id=tenant_id,
            require_review=True
        )

        assert summary["gold_promoted"] == 1
        assert summary["hard_negatives_created"] == 1

        # Check DB states
        gold_items = await gold_repo.get_pending_review(tenant_id=tenant_id)
        assert len(gold_items) == 1
        assert gold_items[0].input_text == "He go."
        assert gold_items[0].review_status == "PENDING"

        neg_items = await hard_neg_repo.get_by_product("english_coach", tenant_id=tenant_id)
        assert len(neg_items) == 1

        assert neg_items[0].input_text == "I has."
        assert neg_items[0].error_bucket == "under_correction"

        await session.rollback()
