import random
from typing import Optional
from app.repositories.prompt_versions import PromptVersionsRepository
from app.repositories.experiments import ExperimentsRepository
from app.db.models import PromptVersion

class PromptRegistryService:
    """Manages system prompt allocations, resolving A/B testing experiment variant splits."""

    def __init__(self, prompt_repo: PromptVersionsRepository, experiment_repo: ExperimentsRepository):
        self.prompt_repo = prompt_repo
        self.experiment_repo = experiment_repo

    async def get_effective_prompt(self, product_id: str, task_id: str) -> Optional[PromptVersion]:
        """Loads prompt templates, resolving A/B experiments weights or falling back to default active versions."""
        # 1. Load active experiments
        experiments = await self.experiment_repo.get_active_experiments()
        
        # 2. Check if this task is mapped to an active experiment variant allocation
        for exp in experiments:
            p_ver = await self.prompt_repo.get_by_id(exp.prompt_version_id)
            if p_ver and p_ver.product_id == product_id and p_ver.task_id == task_id:
                # Random split assignment based on variant weight allocation
                if random.random() < exp.weight:
                    return p_ver

        # 3. Fallback default active template version
        return await self.prompt_repo.get_active_version(product_id, task_id)
