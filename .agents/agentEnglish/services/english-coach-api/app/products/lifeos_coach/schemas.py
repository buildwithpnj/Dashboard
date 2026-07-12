from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator

class LifeOSRespondRequest(BaseModel):
    """API request contract for LifeOS Health Coach."""
    text: str = Field(..., description="The lifestyle update or health query from the user.")
    session_id: Optional[str] = Field(None, description="Optional session or trace identifier.")

    @field_validator("text")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        """Enforces that input cannot be empty or contain only whitespace."""
        if not value or not value.strip():
            raise ValueError("Input text cannot be empty or contain only whitespace.")
        return value

class TokenUsage(BaseModel):
    """Token consumption statistics."""
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    cached_tokens: int = Field(default=0)
    estimated_cost_usd: float = Field(default=0.0)

class LifeOSRespondResponse(BaseModel):
    """API response contract for LifeOS Health Coach."""
    response_id: str = Field(..., description="Unique transaction ID.")
    detected_metrics: Dict[str, Optional[str]] = Field(..., description="Mapped metrics for sleep, diet, activity.")
    analysis: str = Field(..., description="Brief lifestyle assessment.")
    recommendations: List[str] = Field(..., description="Actionable habit tips.")
    disclaimer_triggered: bool = Field(..., description="Flag showing if medical constraints triggered.")
    prompt_version: str = Field(...)
    provider: str = Field(...)
    model: str = Field(...)
    token_usage: TokenUsage = Field(...)
    latency_ms: float = Field(...)
