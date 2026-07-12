import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models import LiveQualityMetric, RegressionEvent
from app.repositories.regression_events import RegressionEventsRepository
from app.services.baseline_comparator import BaselineComparator
from app.services.regression_detector import RegressionDetector

def test_baseline_comparator():
    comparator = BaselineComparator()
    
    baseline = LiveQualityMetric(
        avg_score=0.88,
        pass_rate=0.92,
        escalation_rate=0.01,
        budget_spend=0.50
    )
    current_regressed = LiveQualityMetric(
        avg_score=0.79, # Drop of >5%
        pass_rate=0.86, # Drop of >5%
        escalation_rate=0.04, # Increase of >2%
        budget_spend=0.70 # Increase of >20%
    )
    
    alerts = comparator.compare(current_regressed, baseline)
    assert len(alerts) == 4
    
    triggered_metric_names = [a["metric_name"] for a in alerts if a["triggered"]]
    assert "avg_score" in triggered_metric_names
    assert "pass_rate" in triggered_metric_names
    assert "escalation_rate" in triggered_metric_names
    assert "budget_spend" in triggered_metric_names

@pytest.mark.anyio
async def test_regression_detector_event_logging():
    async with AsyncSessionLocal() as session:
        regression_repo = RegressionEventsRepository(session)
        comparator = BaselineComparator()
        detector = RegressionDetector(regression_repo, comparator)

        tenant_id = f"tenant-{uuid.uuid4()}"
        product_id = "english_coach"

        baseline = LiveQualityMetric(
            avg_score=0.88,
            pass_rate=0.92,
            escalation_rate=0.01,
            budget_spend=0.50
        )
        current = LiveQualityMetric(
            avg_score=0.79,
            pass_rate=0.86,
            escalation_rate=0.04,
            budget_spend=0.70,
            prompt_version="v9.0",
            model_name="mock"
        )

        events = await detector.detect_regressions(
            current=current,
            baseline=baseline,
            tenant_id=tenant_id,
            product_id=product_id
        )

        assert len(events) == 4
        assert events[0].metric_name == "avg_score"
        assert events[0].severity == "warning"

        active = await regression_repo.get_active_events(tenant_id, product_id)
        assert len(active) == 4

        await session.rollback()
