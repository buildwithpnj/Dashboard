import pytest
import uuid
import json
from app.db.session import AsyncSessionLocal
from app.db.models import Base, LearnerProfile, Session, Message, ProductConfig, ApprovedExample
from app.repositories.learner_profiles import LearnerProfilesRepository
from app.repositories.sessions import SessionsRepository
from app.repositories.messages import MessagesRepository
from app.repositories.product_configs import ProductConfigsRepository
from app.repositories.approved_examples import ApprovedExamplesRepository
from app.schemas.evals import ApprovedExample as SchemaApprovedExample

@pytest.mark.anyio
async def test_learner_profiles_repository():
    """Verifies that learner profiles CRUD operations resolve correctly in the database."""
    async with AsyncSessionLocal() as session:
        repo = LearnerProfilesRepository(session)
        user_id = f"test-user-{uuid.uuid4()}"

        profile = LearnerProfile(
            id=f"{user_id}_english_coach",
            user_id=user_id,
            product_id="english_coach",
            summary="Test profile summary info",
            metadata_json="{}"
        )
        await repo.create(profile)

        fetched = await repo.get_by_id(f"{user_id}_english_coach")
        assert fetched is not None
        assert fetched.summary == "Test profile summary info"

        fetched_comp = await repo.get_by_user_and_product(user_id, "english_coach")
        assert fetched_comp is not None
        assert fetched_comp.user_id == user_id

        await session.rollback()

@pytest.mark.anyio
async def test_product_configs_repository():
    """Verifies that product configs read operations resolve config rows."""
    async with AsyncSessionLocal() as session:
        repo = ProductConfigsRepository(session)
        product_id = f"prod-{uuid.uuid4()}"

        config = ProductConfig(
            id=product_id,
            name="Test Coach",
            description="Testing prompts template",
            prompt_template="System prompt templates",
            max_dynamic_tokens=100
        )
        await repo.create(config)

        fetched = await repo.get_by_id(product_id)
        assert fetched is not None
        assert fetched.name == "Test Coach"

        active_list = await repo.get_active_configs()
        assert len(active_list) > 0

        await session.rollback()

@pytest.mark.anyio
async def test_approved_examples_repository_db_mode():
    """Verifies database reads and writes in the approved examples dual-mode repository."""
    async with AsyncSessionLocal() as session:
        repo = ApprovedExamplesRepository(db_session=session)
        ex_id = f"ex-{uuid.uuid4()}"

        schema_ex = SchemaApprovedExample(
            id=ex_id,
            input_text="broken input text",
            natural_english="natural corrected output",
            professional_english="professional corrected output",
            tags=["tag-test"],
            created_at="2026-07-12T12:00:00.000000Z"
        )
        await repo.add_example(schema_ex)

        all_ex = await repo.get_all(product_id="tag-test")
        assert len(all_ex) > 0
        assert all_ex[0].id == ex_id
        assert all_ex[0].natural_english == "natural corrected output"

        await session.rollback()

@pytest.mark.anyio
async def test_embedding_service():
    """Asserts that the embedding service returns the correct mock dimension count offline."""
    from app.services.embedding_service import EmbeddingService
    service = EmbeddingService()
    emb = await service.get_embedding("hello test world")
    assert isinstance(emb, list)
    assert len(emb) == 1536

@pytest.mark.anyio
async def test_vector_memory_repository_sqlite_mode():
    """Asserts that the vector repository handles SQLite fallback dialect gracefully."""
    from app.repositories.vector_memory import VectorMemoryRepository
    async with AsyncSessionLocal() as session:
        repo = VectorMemoryRepository(session)
        
        # Test add vector fallback
        await repo.add_vector("v-01", "hello", [0.1]*1536, {})
        
        # Test search fallback
        results = await repo.search_similar([0.1]*1536)
        assert results == []
        
        await session.rollback()
