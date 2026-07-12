import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models import PromptVersion, Experiment
from app.repositories.prompt_versions import PromptVersionsRepository
from app.repositories.experiments import ExperimentsRepository
from app.services.prompt_registry import PromptRegistryService

@pytest.mark.anyio
async def test_ab_experiment_allocations():
    """Asserts that prompt registry dynamically retrieves experiment variants when active."""
    async with AsyncSessionLocal() as db:
        prompt_repo = PromptVersionsRepository(db)
        exp_repo = ExperimentsRepository(db)
        
        # 1. Create a variant prompt version
        p_id = str(uuid.uuid4())
        pv = PromptVersion(
            id=p_id,
            product_id="english_coach",
            task_id="correction",
            version="v2.5_experiment",
            prompt_template="Experiment template: {text}",
            is_active=False
        )
        await prompt_repo.create(pv)
        
        # 2. Create an active experiment with 100% allocation weight (always routes to it)
        exp = Experiment(
            id=str(uuid.uuid4()),
            name="Test A/B Experiment",
            prompt_version_id=p_id,
            weight=1.0,
            is_active=True
        )
        await exp_repo.create(exp)
        await db.commit()

        # 3. Resolve effective prompt
        registry = PromptRegistryService(prompt_repo, exp_repo)
        resolved = await registry.get_effective_prompt("english_coach", "correction")
        assert resolved is not None
        assert resolved.id == p_id

        # Cleanup
        await exp_repo.delete(exp)
        await prompt_repo.delete(pv)
        await db.commit()
