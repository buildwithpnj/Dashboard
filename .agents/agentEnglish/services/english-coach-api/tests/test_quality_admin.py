import pytest
import jwt
import uuid
import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models import LiveQualityMetric, FailureTrend, RegressionEvent, PromptVersion, BatchEvalRun

client = TestClient(app)

@pytest.mark.anyio
async def test_quality_admin_endpoints():
    """Asserts that quality monitoring, failure trends, active alerts and rollback APIs are fully functional."""
    old_auth_state = settings.AUTH_ENABLED
    settings.AUTH_ENABLED = True
    
    tenant_id = f"tenant-quality-{uuid.uuid4()}"
    product_id = f"product-{uuid.uuid4()}"
    event_id = str(uuid.uuid4())
    metric_id = str(uuid.uuid4())
    trend_id = str(uuid.uuid4())
    
    try:
        # 1. Seed historical metrics, failure trends, active alerts and versions in DB
        async with AsyncSessionLocal() as db:
            # Seed LiveQualityMetric
            metric = LiveQualityMetric(
                id=metric_id,
                tenant_id=tenant_id,
                product_id=product_id,
                model_name="mock",
                prompt_version="v2.0",
                window_size="24h",
                avg_score=0.74,
                pass_rate=0.86,
                escalation_rate=0.04,
                review_queue_rate=0.10,
                budget_spend=0.70,
                token_usage=20,
                created_at=datetime.datetime.utcnow()
            )
            db.add(metric)
            
            # Seed FailureTrend
            trend = FailureTrend(
                id=trend_id,
                tenant_id=tenant_id,
                product_id=product_id,
                error_bucket="under_correction",
                count=3,
                window_size="24h",
                created_at=datetime.datetime.utcnow()
            )
            db.add(trend)
            
            # Seed RegressionEvent
            event = RegressionEvent(
                id=event_id,
                tenant_id=tenant_id,
                product_id=product_id,
                metric_name="avg_score",
                baseline_value=0.88,
                current_value=0.74,
                threshold_crossed=0.05,
                severity="warning",
                prompt_version="v2.0",
                model_name="mock",
                status="ACTIVE",
                created_at=datetime.datetime.utcnow()
            )
            db.add(event)
            
            # Seed PromptVersions
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
            db.add(v1)
            db.add(v2)
            
            # Seed BatchEvalRun for v1.0 (rollback recommendation target)
            run_v1 = BatchEvalRun(
                id=str(uuid.uuid4()),
                dataset_name="jfleg",
                tenant_id=tenant_id,
                product_id=product_id,
                status="COMPLETED",
                prompt_version="v1.0",
                avg_score=0.92,
                model_name="mock"
            )
            db.add(run_v1)
            
            await db.commit()

        # Generate admin token
        token = jwt.encode(
            {"sub": "admin_user", "role": "admin", "tenant_id": tenant_id},
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Test GET /v1/admin/quality/rolling-metrics
        res = client.get(f"/v1/admin/quality/rolling-metrics?product_id={product_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        assert data[0]["id"] == metric_id
        assert data[0]["avg_score"] == 0.74

        # 3. Test GET /v1/admin/quality/failure-trends
        res = client.get(f"/v1/admin/quality/failure-trends?product_id={product_id}&window_size=24h", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        assert data[0]["id"] == trend_id
        assert data[0]["error_bucket"] == "under_correction"

        # 4. Test GET /v1/admin/quality/alerts
        res = client.get(f"/v1/admin/quality/alerts?product_id={product_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        assert data[0]["id"] == event_id
        assert data[0]["status"] == "ACTIVE"

        # 5. Test POST /v1/admin/quality/rollback/recommend
        res = client.post(
            "/v1/admin/quality/rollback/recommend",
            json={"event_id": event_id},
            headers=headers
        )
        assert res.status_code == 200
        plan = res.json()
        assert plan["event_id"] == event_id
        assert plan["recommended_version"] == "v1.0"
        assert "v1.0" in plan["message"]

        # 6. Test POST /v1/admin/quality/rollback/approve
        res = client.post(
            "/v1/admin/quality/rollback/approve",
            json={"plan": plan},
            headers=headers
        )
        assert res.status_code == 200
        assert res.json()["status"] == "success"
        assert "v1.0" in res.json()["message"]

        # Check that RegressionEvent status is now RESOLVED in DB
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            stmt = select(RegressionEvent).filter(RegressionEvent.id == event_id)
            res_db = await db.execute(stmt)
            updated_event = res_db.scalars().first()
            assert updated_event.status == "RESOLVED"

    finally:
        settings.AUTH_ENABLED = old_auth_state
        # Clean up database records
        async with AsyncSessionLocal() as db:
            from sqlalchemy import delete
            await db.execute(delete(LiveQualityMetric).filter(LiveQualityMetric.tenant_id == tenant_id))
            await db.execute(delete(FailureTrend).filter(FailureTrend.tenant_id == tenant_id))
            await db.execute(delete(RegressionEvent).filter(RegressionEvent.tenant_id == tenant_id))
            await db.execute(delete(PromptVersion).filter(PromptVersion.product_id == product_id))
            await db.execute(delete(BatchEvalRun).filter(BatchEvalRun.tenant_id == tenant_id))
            await db.commit()
