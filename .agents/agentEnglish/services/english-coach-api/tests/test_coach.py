def test_coach_respond_schema_validation(client):
    """Verifies that the response matches the expected Pydantic CoachRespondResponse schema and fields."""
    response = client.post(
        "/v1/coach/respond",
        json={"text": "kal client ko update dena hai"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Required schema fields check
    assert "detected_input_style" in data
    assert "intent" in data
    assert "natural_english" in data
    assert "professional_english" in data
    assert "explanation" in data
    assert "ambiguity" in data
    assert "clarification_question" in data
    assert "mistake_tags" in data
    assert "confidence" in data
    assert "prompt_version" in data
    assert "provider" in data
    assert "model" in data
    assert "token_usage" in data
    assert "latency_ms" in data
    
    # Token usage details check
    token_usage = data["token_usage"]
    assert "input_tokens" in token_usage
    assert "output_tokens" in token_usage
    assert "cached_tokens" in token_usage
    assert "estimated_cost_usd" in token_usage

def test_coach_respond_ambiguous_text(client):
    """Verifies that ambiguous queries raise the ambiguity flag and prompt questions."""
    response = client.post(
        "/v1/coach/respond",
        json={"text": "kal usko bol dena"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["ambiguity"] is True
    assert data["clarification_question"] is not None
    assert data["natural_english"] is None
    assert data["professional_english"] is None

def test_coach_respond_empty_input_fails(client):
    """Verifies that sending empty or whitespace-only inputs yields a 422 validation failure."""
    response = client.post(
        "/v1/coach/respond",
        json={"text": "   "}
    )
    assert response.status_code == 422
    
    response_empty = client.post(
        "/v1/coach/respond",
        json={"text": ""}
    )
    assert response_empty.status_code == 422

def test_coach_respond_professional_rewrite(client):
    """Verifies that rewrite intents generate correct outputs and tag professional parameters."""
    response = client.post(
        "/v1/coach/respond",
        json={"text": "rewrite this please"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "rewrite_professional"
    assert data["detected_input_style"] == "English"
    assert "tone" in data["mistake_tags"]

def test_coach_respond_correction_explanation(client):
    """Verifies that broken English correction lists explanation comments and mistake tags."""
    response = client.post(
        "/v1/coach/respond",
        json={"text": "i am not able to join because network issue tha"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_input_style"] == "Mixed"
    assert data["intent"] == "correct"
    assert data["explanation"] is not None
    assert len(data["mistake_tags"]) > 0

def test_coach_feedback_loop(client):
    """Verifies that the user feedback route returns a successful confirmation message."""
    from app.services.feedback_service import FeedbackService
    FeedbackService.register_transaction(
        response_id="uuid-spec-99",
        input_text="original query",
        natural_english="natural",
        professional_english="professional",
        tags=["tag"]
    )
    
    payload = {
        "response_id": "uuid-spec-99",
        "approved": True,
        "corrected_text": "I was unable to join because of a network issue.",
        "comments": "Very good suggestions"
    }
    response = client.post("/v1/coach/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Feedback captured" in data["message"]

