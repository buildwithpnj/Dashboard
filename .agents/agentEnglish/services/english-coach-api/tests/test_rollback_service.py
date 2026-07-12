import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models import PromptVersion, BatchEvalRun, RegressionEvent
from app.services.version_recommender import VersionRecommender
from app.services.rollback_service import RollbackService

@pytest.mark.anyio
async def test_rollback_service_recommendation():
    async with AsyncSessionLocal() as session:
        recommender = VersionRecommender(session)
        service = RollbackService(recommender)

        tenant_id = f"tenant-{uuid.uuid4()}"
        product_id = "english_coach"

        # 1. Create prompt versions and eval runs history
        v1 = PromptVersion(
            id=str(uuid.uuid4()),
            product_id=product_id,
            task_id="correction",
            version="v1.0",
            prompt_template="Translate {text}",
            is_active=False
        )
        v2 = PromptVersion(
            id=str(uuid.uuid4()),
            product_id=product_id,
            task_id="correction",
            version="v2.0",
            prompt_template="Coaching {text}",
            is_active=True
        )
        session.add(v1)
        session.add(v2)

        # Seeding high historical runs for v1.0
        run_v1 = BatchEvalRun(
            id=str(uuid.uuid4()),
            dataset_name="jfleg",
            tenant_id=tenant_id,
            product_id=product_id,
            status="COMPLETED",
            prompt_version="v1.0",
            avg_score=0.92,  # Best score winner
            model_name="mock"
        )
        # Seeding low runs for v2.0
        run_v2 = BatchEvalRun(
            id=str(uuid.uuid4()),
            dataset_name="jfleg",
            tenant_id=tenant_id,
            product_id=product_id,
            status="COMPLETED",
            prompt_version="v2.0",
            avg_score=0.74,
            model_name="mock"
        )
        session.add(run_v1)
        session.add(run_v2)
        await session.flush()

        # 2. Run rollback suggestions check
        event = RegressionEvent(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            product_id=product_id,
            metric_name="avg_score",
            baseline_value=0.88,
            current_value=0.74,
            prompt_version="v2.0",
            model_name="mock"
        )

        plan = await service.evaluate_rollback(event)
        assert plan is not None
        assert plan["recommended_version"] == "v1.0"
        assert "v1.0" in plan["message"]

        await session.rollback()
