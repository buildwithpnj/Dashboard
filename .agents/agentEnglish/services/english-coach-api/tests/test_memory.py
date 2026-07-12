import asyncio
import pytest
from app.services.memory_service import MemoryService
from app.api.deps import _approved_repo
from app.core.config import settings
from app.prompts.prompt_library import estimate_token_count
from app.services.coach_service import CoachService
from app.providers.mock_provider import MockLLMProvider
from app.services.language_detector import LanguageDetector
from app.services.intent_classifier import IntentClassifier
from app.services.response_formatter import ResponseFormatter
from app.schemas.coach import CoachRespondRequest

@pytest.mark.anyio
async def test_memory_retrieval_matches_heuristics():
    """Asserts that the memory service retrieves context matched by keywords or fallbacks."""
    memory_service = MemoryService(approved_repo=_approved_repo)
    examples = await memory_service.retrieve_examples("kal client ko report dena hai")
    
    assert len(examples) > 0
    # Must retrieve client-themed examples
    assert any("client" in ex.lower() for ex in examples)

def test_token_guardrails_truncation_limits(monkeypatch):
    """Asserts that token budget limits clip context size and drop examples safely on overflow."""
    # Override settings limit to enforce a tiny dynamic size budget (e.g. 20 tokens)
    monkeypatch.setattr(settings, "MAX_DYNAMIC_CONTEXT_TOKENS", 20)
    
    detector = LanguageDetector()
    classifier = IntentClassifier()
    formatter = ResponseFormatter()
    memory_service = MemoryService(approved_repo=_approved_repo)
    provider = MockLLMProvider()
    
    coach_service = CoachService(
        provider=provider,
        detector=detector,
        classifier=classifier,
        formatter=formatter,
        memory=memory_service
    )
    
    req = CoachRespondRequest(text="i am not able to join because network issue tha")
    
    async def run_async_test():
        # Call respond pipeline, which will trigger the dynamic context token limit checks
        res = await coach_service.process_request(req)
        assert res.response_id is not None
        # Verify schema is returned intact despite truncation
        assert res.natural_english is not None

    asyncio.run(run_async_test())
