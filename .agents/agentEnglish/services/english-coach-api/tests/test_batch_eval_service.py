import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.repositories.batch_eval_runs import BatchEvalRunsRepository
from app.repositories.eval_examples import EvalExamplesRepository
from app.services.batch_eval_service import BatchEvalService

@pytest.mark.anyio
async def test_batch_eval_service_execution():
    async with AsyncSessionLocal() as session:
        runs_repo = BatchEvalRunsRepository(session)
        examples_repo = EvalExamplesRepository(session)
        service = BatchEvalService(runs_repo, examples_repo)

        # Setup test data
        examples = [
            {"source_text": "He go to school.", "reference_corrections": ["He went to school."], "task_type": "correction"},
            {"source_text": "She play tennis.", "reference_corrections": ["She plays tennis."], "task_type": "correction"}
        ]

        run = await service.create_run(
            dataset_name="test_dataset",
            product_id="english_coach",
            examples=examples,
            budget_limit_usd=1.0,
            model_name="mock"
        )
        assert run.status == "PENDING"
        assert run.total_examples == 2

        # Run execution
        summary = await service.execute_run(
            run_id=run.id,
            examples=examples,
            batch_size=1,
            mock_model_fn=lambda x: "He went to school." if "go" in x else "She plays tennis."
        )

        assert summary["status"] == "COMPLETED"
        assert summary["processed"] == 2
        assert summary["passed"] == 2

        # Check DB states
        updated_run = await runs_repo.get_by_id(run.id)
        assert updated_run.status == "COMPLETED"
        assert updated_run.processed_count == 2
        
        saved_items = await examples_repo.get_by_run(run.id)
        assert len(saved_items) == 2
        assert saved_items[0].composite_score >= 0.5

        await session.rollback()
