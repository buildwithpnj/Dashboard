from typing import Optional
from app.db.models import RegressionEvent
from app.services.version_recommender import VersionRecommender

class RollbackService:
    """Evaluates performance regressions and prepares rollback plans for prompt/model versions."""

    def __init__(self, recommender: VersionRecommender):
        self.recommender = recommender

    async def evaluate_rollback(self, regression_event: RegressionEvent) -> Optional[dict]:
        """
        Recommends a rollback version using the VersionRecommender.
        If a rollback is found, returns a rollback plan suggestion:
        {"event_id": str, "recommended_version": str, "model_name": str, "message": str}
        """
        recommendation = await self.recommender.recommend_rollback_version(
            product_id=regression_event.product_id,
            tenant_id=regression_event.tenant_id
        )
        if not recommendation:
            return None

        rec_version = recommendation["prompt_version"]
        model_name = recommendation["model_name"]

        message = (
            f"Rollback to prompt version {rec_version} utilizing model {model_name} is recommended "
            f"due to regression event '{regression_event.id}' ({regression_event.metric_name}). "
            f"Note: This rollback requires administrator approval before auto-deployment."
        )

        return {
            "event_id": regression_event.id,
            "recommended_version": rec_version,
            "model_name": model_name,
            "message": message
        }
