import pytest
import uuid
import datetime
from app.db.session import AsyncSessionLocal
from app.db.models import EvalExampleResult, LiveQualityMetric, FailureTrend
from app.repositories.live_quality_metrics import LiveQualityMetricsRepository
from app.repositories.failure_trends import FailureTrendsRepository
from app.services.live_quality_monitor import LiveQualityMonitor

@pytest.mark.anyio
async def test_live_quality_monitor_aggregation():
    async with AsyncSessionLocal() as session:
        metrics_repo = LiveQualityMetricsRepository(session)
        trends_repo = FailureTrendsRepository(session)
        monitor = LiveQualityMonitor(metrics_repo, trends_repo)

        tenant_id = f"tenant-{uuid.uuid4()}"
        product_id = "english_coach"
        run_id = f"run-{uuid.uuid4()}"

        # 1. Setup sample example outputs within time window
        now = datetime.datetime.utcnow()
        ex1 = EvalExampleResult(
            id=str(uuid.uuid4()),
            run_id=run_id,
            example_hash="hash1",
            task_type="correction",
            input_text="He go.",
            model_output="He went.",
            composite_score=0.90,
            status="SCORED",
            cost_usd=0.005,
            tokens_used=10,
            created_at=now
        )
        ex2 = EvalExampleResult(
            id=str(uuid.uuid4()),
            run_id=run_id,
            example_hash="hash2",
            task_type="correction",
            input_text="I has.",
            model_output="I has.",
            composite_score=0.30,
            status="SCORED",
            error_bucket="under_correction",
            cost_usd=0.005,
            tokens_used=10,
            created_at=now
        )
        session.add(ex1)
        session.add(ex2)
        await session.flush()

        # 2. Run aggregate_period
        metric = await monitor.aggregate_period(
            tenant_id=tenant_id,
            product_id=product_id,
            window_size="24h",
            start_time=now - datetime.timedelta(hours=1),
            end_time=now + datetime.timedelta(hours=1),
            db_session=session
        )

        assert metric.avg_score == 0.60
        assert metric.pass_rate == 0.50
        assert metric.budget_spend == 0.010
        assert metric.token_usage == 20

        # Check failure trends were logged
        trends = await trends_repo.get_trends(tenant_id, product_id, "24h")
        assert len(trends) == 1
        assert trends[0].error_bucket == "under_correction"
        assert trends[0].count == 1

        await session.rollback()
