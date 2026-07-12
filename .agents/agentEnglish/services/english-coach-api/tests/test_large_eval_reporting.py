import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.repositories.error_clusters import ErrorClustersRepository
from app.services.failure_bucket_analyzer import FailureBucketAnalyzer

@pytest.mark.anyio
async def test_failure_bucket_reporting():
    async with AsyncSessionLocal() as session:
        error_repo = ErrorClustersRepository(session)
        analyzer = FailureBucketAnalyzer(error_repo)

        run_id = f"run-{uuid.uuid4()}"
        results = [
            {"error_bucket": "wrong_correction"},
            {"error_bucket": "wrong_correction"},
            {"error_bucket": "too_verbose"},
            {"error_bucket": None}
        ]

        # 1. Aggregate
        aggregated = await analyzer.aggregate_failures(
            run_id=run_id,
            results=results,
            dataset_name="jfleg",
            model_name="mock",
            product_id="english_coach"
        )

        assert len(aggregated) == 2
        assert aggregated[0]["bucket_name"] == "wrong_correction"
        assert aggregated[0]["count"] == 2
        assert aggregated[1]["bucket_name"] == "too_verbose"
        assert aggregated[1]["count"] == 1

        # 2. Report generation format validation
        report = analyzer.generate_report(aggregated, "jfleg", "mock")
        assert "wrong_correction" in report
        assert "too_verbose" in report

        await session.rollback()
