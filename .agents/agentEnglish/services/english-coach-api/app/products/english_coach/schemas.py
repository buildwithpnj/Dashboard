from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class CoachRespondRequest(BaseModel):
    """API request contract for English Coach."""
    text: str = Field(..., description="The input text to translate, correct, or rewrite.")
    session_id: Optional[str] = Field(None, description="Optional session or trace identifier.")

    @field_validator("text")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        """Enforces that input cannot be empty or contain only whitespace."""
        if not value or not value.strip():
            raise ValueError("Input text cannot be empty or contain only whitespace.")
        return value

class TokenUsage(BaseModel):
    """Token usage and API cost summary."""
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    cached_tokens: int = Field(default=0)
    estimated_cost_usd: float = Field(default=0.0)

class CoachRespondResponse(BaseModel):
    """Structured response return schema for English Coach."""
    response_id: str = Field(..., description="Unique transaction ID.")
    detected_input_style: str = Field(...)
    intent: str = Field(...)
    natural_english: Optional[str] = Field(None)
    professional_english: Optional[str] = Field(None)
    explanation: Optional[str] = Field(None)
    ambiguity: bool = Field(...)
    clarification_question: Optional[str] = Field(None)
    mistake_tags: List[str] = Field(default_factory=list)
    confidence: float = Field(...)
    prompt_version: str = Field(...)
    provider: str = Field(...)
    model: str = Field(...)
    token_usage: TokenUsage = Field(...)
    latency_ms: float = Field(...)

class CoachFeedbackRequest(BaseModel):
    """User feedback request contract."""
    response_id: str = Field(..., description="Transaction response UUID.")
    approved: bool = Field(...)
    corrected_text: Optional[str] = Field(None)
    comments: Optional[str] = Field(None)

class CoachFeedbackResponse(BaseModel):
    """Feedback logging response status."""
    status: str = Field("success")
    message: str = Field(...)
