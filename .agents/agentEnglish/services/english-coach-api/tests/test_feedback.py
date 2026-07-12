from app.services.feedback_service import FeedbackService
from app.api.deps import _approved_repo

import pytest

@pytest.mark.anyio
async def test_feedback_loop_persistence_and_lookup(client):
    """Verifies that approved feedback successfully appends new examples to the repository database."""
    # 1. Register a fake mock transaction to verify loop mapping
    test_id = "uuid-test-feedback-loop-1"
    FeedbackService.register_transaction(
        response_id=test_id,
        input_text="kal chutti chahiye",
        natural_english="I want a holiday tomorrow.",
        professional_english="I request leave for tomorrow.",
        tags=["translation"]
    )

    # 2. Get database size prior to appending
    existing_examples = await _approved_repo.get_all()
    size_before = len(existing_examples)

    # 3. Post user feedback request
    payload = {
        "response_id": test_id,
        "approved": True,
        "corrected_text": "I need leave tomorrow.",
        "comments": "Perfect translation feedback test."
    }
    response = client.post("/v1/coach/feedback", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "Feedback captured successfully" in data["message"]

    # 4. Assert new example was saved in repository file
    updated_examples = await _approved_repo.get_all()
    assert len(updated_examples) == size_before + 1

    last_example = updated_examples[-1]
    assert last_example.input_text == "kal chutti chahiye"
    # Natural english is overridden by corrected_text payload
    assert last_example.natural_english == "I need leave tomorrow."
    # Professional english inherits from transaction caches
    assert last_example.professional_english == "I request leave for tomorrow."
    assert last_example.tags == ["translation"]

    # 5. Clean up repository database to prevent test run leftovers
    _approved_repo._overwrite_all([ex.model_dump() for ex in existing_examples])
