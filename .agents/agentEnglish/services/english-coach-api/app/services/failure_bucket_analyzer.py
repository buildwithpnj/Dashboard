import logging
import uuid
from typing import List, Dict, Any
from app.db.models import ErrorCluster
from app.repositories.error_clusters import ErrorClustersRepository

logger = logging.getLogger(__name__)

class FailureBucketAnalyzer:
    """Aggregates individual example failure flags into structured counts clusters."""

    def __init__(self, error_clusters_repo: ErrorClustersRepository):
        self.error_clusters_repo = error_clusters_repo

    async def aggregate_failures(
        self,
        run_id: str,
        results: List[Any],
        dataset_name: str = "unknown",
        model_name: str = "mock",
        product_id: str = "english_coach",
        prompt_version: str = "v1.0"
    ) -> List[Dict[str, Any]]:
        """Groups example results by their tagged error buckets and persists aggregate clusters."""
        bucket_counts: Dict[str, int] = {}
        total = len(results)

        for res in results:
            # Handle both model objects and dict inputs
            bucket = getattr(res, "error_bucket", None) or (res.get("error_bucket") if isinstance(res, dict) else None)
            if bucket:
                bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

        aggregated = []
        for bucket, count in bucket_counts.items():
            pct = (count / total * 100.0) if total > 0 else 0.0
            aggregated.append({
                "bucket_name": bucket,
                "count": count,
                "percentage": round(pct, 2)
            })

            # Create ErrorCluster ORM record
            cluster = ErrorCluster(
                id=str(uuid.uuid4()),
                run_id=run_id,
                bucket_name=bucket,
                count=count,
                dataset_name=dataset_name,
                model_name=model_name,
                product_id=product_id,
                prompt_version=prompt_version
            )
            await self.error_clusters_repo.create(cluster)

        # Sort descending by count
        aggregated.sort(key=lambda x: x["count"], reverse=True)
        return aggregated

    def generate_report(self, aggregated: List[Dict[str, Any]], dataset_name: str, model_name: str) -> str:
        """Constructs a visual console table reporting the failure distribution."""
        header = f"=== FAILURE DISTRIBUTION: {dataset_name} ({model_name}) ==="
        divider = "-" * len(header)
        lines = [header, divider]
        lines.append(f"{'Error Category':<25} | {'Count':<5} | {'Percentage':<10}")
        lines.append(divider)
        for item in aggregated:
            lines.append(f"{item['bucket_name']:<25} | {item['count']:<5} | {item['percentage']:.2f}%")
        lines.append(divider)
        return "\n".join(lines)
