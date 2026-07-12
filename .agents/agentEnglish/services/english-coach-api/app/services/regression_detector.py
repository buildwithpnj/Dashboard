import uuid
import datetime
from typing import List
from app.db.models import LiveQualityMetric, RegressionEvent
from app.repositories.regression_events import RegressionEventsRepository
from app.services.baseline_comparator import BaselineComparator

class RegressionDetector:
    """Detects metric regressions by comparing rolling metrics to baselines and records regression events."""

    def __init__(self, regression_repo: RegressionEventsRepository, comparator: BaselineComparator):
        self.regression_repo = regression_repo
        self.comparator = comparator

    async def detect_regressions(
        self,
        current: LiveQualityMetric,
        baseline: LiveQualityMetric,
        tenant_id: str,
        product_id: str
    ) -> List[RegressionEvent]:
        """
        Runs comparator.compare.
        For each triggered alert, creates and saves a RegressionEvent using regression_repo.
        Returns list of created RegressionEvents.
        """
        alerts = self.comparator.compare(current, baseline)
        created_events = []

        # Threshold mappings for threshold_crossed logging
        threshold_map = {
            "avg_score": {"warning": 0.05, "critical": 0.10},
            "pass_rate": 0.05,
            "escalation_rate": 0.02,
            "budget_spend": 0.20
        }

        for alert in alerts:
            if alert["triggered"]:
                metric = alert["metric_name"]
                sev = alert["severity"]
                
                # Retrieve corresponding threshold crossed value
                if metric == "avg_score":
                    threshold = threshold_map["avg_score"][sev]
                else:
                    threshold = threshold_map.get(metric, 0.0)

                event = RegressionEvent(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    product_id=product_id,
                    metric_name=metric,
                    baseline_value=alert["baseline"],
                    current_value=alert["current"],
                    threshold_crossed=float(threshold),
                    severity=sev,
                    prompt_version=current.prompt_version or "unknown",
                    model_name=current.model_name or "unknown",
                    status="ACTIVE",
                    created_at=datetime.datetime.utcnow()
                )
                
                saved_event = await self.regression_repo.create(event)
                created_events.append(saved_event)

        return created_events
