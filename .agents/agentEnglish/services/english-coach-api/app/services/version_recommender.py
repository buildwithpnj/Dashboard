from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import PromptVersion, BatchEvalRun, LiveQualityMetric

class VersionRecommender:
    """Scans historical run metrics to recommend optimal prompt versions for fallback/rollback actions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def recommend_rollback_version(self, product_id: str, tenant_id: str) -> Optional[dict]:
        """
        Scans prompt versions for the given product_id and suggests the version 
        with the highest average historical composite_score from evaluation runs or metrics.
        
        Returns:
            dict: {"prompt_version": str, "model_name": str, "avg_historical_score": float, "reason": str}
            or None if no rollback candidates are found.
        """
        # 1. Fetch all PromptVersions for this product
        stmt_pv = select(PromptVersion).filter(PromptVersion.product_id == product_id)
        res_pv = await self.db.execute(stmt_pv)
        prompt_versions = res_pv.scalars().all()
        
        if not prompt_versions:
            return None

        pv_versions = {pv.version for pv in prompt_versions}
        active_version = next((pv.version for pv in prompt_versions if pv.is_active), None)

        # 2. Fetch all BatchEvalRun records for product and tenant
        stmt_run = select(BatchEvalRun).filter(
            BatchEvalRun.product_id == product_id,
            BatchEvalRun.tenant_id == tenant_id
        )
        res_run = await self.db.execute(stmt_run)
        runs = res_run.scalars().all()

        version_scores: Dict[str, List[float]] = {}
        version_models: Dict[str, str] = {}

        for r in runs:
            if not r.prompt_version:
                continue
            # avg_score is a float column we added to BatchEvalRun
            version_scores.setdefault(r.prompt_version, []).append(r.avg_score)
            if r.model_name:
                version_models[r.prompt_version] = r.model_name

        # 3. Fetch all LiveQualityMetric records to complement historical performance data
        stmt_metric = select(LiveQualityMetric).filter(
            LiveQualityMetric.product_id == product_id,
            LiveQualityMetric.tenant_id == tenant_id
        )
        res_metric = await self.db.execute(stmt_metric)
        metrics = res_metric.scalars().all()

        for m in metrics:
            if not m.prompt_version:
                continue
            version_scores.setdefault(m.prompt_version, []).append(m.avg_score)
            if m.model_name:
                version_models[m.prompt_version] = m.model_name

        # 4. Calculate average score for each version and filter candidates
        candidates = []
        for ver in pv_versions:
            # We skip the currently active/regressed version to find a rollback version
            if active_version and ver == active_version:
                continue
            
            scores = version_scores.get(ver)
            if scores:
                avg_score = sum(scores) / len(scores)
                candidates.append((ver, avg_score))

        if not candidates:
            return None

        # 5. Suggest candidate with highest average score
        best_ver, best_score = max(candidates, key=lambda x: x[1])
        model_name = version_models.get(best_ver, "mock")
        reason = f"Version {best_ver} has the highest average historical composite score of {best_score:.4f}."

        return {
            "prompt_version": best_ver,
            "model_name": model_name,
            "avg_historical_score": float(best_score),
            "reason": reason
        }
