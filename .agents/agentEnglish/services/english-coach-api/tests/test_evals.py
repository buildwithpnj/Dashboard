import os
import pytest
from app.services.scoring import ScoringEngine, calculate_jaccard_similarity
from app.schemas.evals import EvalCase
from app.schemas.coach import CoachRespondResponse, TokenUsage
from app.services.eval_service import EvalService
from app.api.deps import get_coach_service, get_llm_provider
from app.repositories.eval_runs import EvalRunsRepository

def test_jaccard_similarity_calculation():
    """Assert Jaccard similarity computes overlap ratio correctly."""
    s1 = "hello world"
    s2 = "hello world"
    assert calculate_jaccard_similarity(s1, s2) == 1.0
    
    s3 = "hello world universe"
    assert calculate_jaccard_similarity(s1, s3) == 2.0 / 3.0
    
    # Assert whitespace and casings don't affect similarity
    s4 = "Hello, World!"
    assert calculate_jaccard_similarity(s1, s4) == 1.0

def test_scoring_dimensions_perfect():
    """Assert scoring metrics evaluate perfectly matched responses at 100%."""
    engine = ScoringEngine()
    case = EvalCase(
        id="test_case_1",
        input_text="kal client ko update dena hai",
        expected_style="Hinglish",
        expected_intent="translate",
        expected_ambiguity=False,
        reference_natural="We need to update the client tomorrow.",
        reference_professional="We are scheduled to provide an update to the client tomorrow.",
        tags=["translation"]
    )

    response = CoachRespondResponse(
        response_id="uuid-test-99",
        detected_input_style="Hinglish",
        intent="translate",
        natural_english="We need to update the client tomorrow.",
        professional_english="We are scheduled to provide an update to the client tomorrow.",
        explanation="Translated Hinglish to English correctly.",
        ambiguity=False,
        clarification_question=None,
        mistake_tags=[],
        confidence=0.98,
        prompt_version="v0.1",
        provider="MockLLMProvider",
        model="gpt-4o-mini",
        token_usage=TokenUsage(),
        latency_ms=12.0
    )

    scores = engine.score_response(case, response)
    assert scores["meaning_preservation"] == 1.0
    assert scores["tone_match"] == 1.0
    assert scores["ambiguity_handling"] == 1.0
    assert scores["explanation_quality"] == 1.0

    weighted = engine.calculate_weighted_score(scores)
    assert weighted == 1.0

@pytest.mark.anyio
async def test_eval_case_loading_from_disk():
    """Assert that seeded JSONL test files load cleanly into EvalCase structures."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    eval_file = os.path.join(workspace_root, "data", "evals", "translation_eval.jsonl")

    provider = get_llm_provider()
    coach_service = await get_coach_service(provider=provider)
    runs_repo = EvalRunsRepository(output_dir=os.path.join(script_dir, "output"))
    scoring_engine = ScoringEngine()
    eval_service = EvalService(coach_service, runs_repo, scoring_engine)

    cases = eval_service.load_cases_from_jsonl(eval_file)
    assert len(cases) > 0
    assert cases[0].id == "trans_01"
    assert cases[0].expected_style == "Hinglish"
    assert cases[0].expected_intent == "translate"
