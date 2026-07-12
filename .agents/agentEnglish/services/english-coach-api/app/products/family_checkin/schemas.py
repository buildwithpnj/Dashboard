from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator

class ContactInfo(BaseModel):
    """Escalation contact details."""
    name: str = Field(..., description="Contact person name.")
    phone: str = Field(..., description="Contact phone number.")
    relationship: str = Field(..., description="Relationship context (e.g. Son, Daughter, Neighbor).")

class FamilyCheckinRequest(BaseModel):
    """API request contract for Family Check-in agent."""
    user_id: str = Field(..., description="User ID corresponding to the parent settings profile.")
    message_text: str = Field(..., description="Message string received from the parent.")
    session_id: Optional[str] = Field(None, description="Optional session track identifier.")

    @field_validator("message_text")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        """Enforces that input cannot be empty or contain only whitespace."""
        if not value or not value.strip():
            raise ValueError("Input message text cannot be empty or contain only whitespace.")
        return value

class TokenUsage(BaseModel):
    """Token statistics."""
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    cached_tokens: int = Field(default=0)
    estimated_cost_usd: float = Field(default=0.0)

class FamilyCheckinResponse(BaseModel):
    """API response contract for Family Check-in agent."""
    response_id: str = Field(..., description="Unique transaction ID.")
    checkin_status: str = Field(..., description="Status category: normal | flagged | escalated.")
    response_text: str = Field(..., description="Caring reply generated for the parent.")
    notes: Optional[str] = Field(None, description="Internal audit commentary notes.")
    escalation_triggered: bool = Field(..., description="Flag showing if escalation triggers active.")
    escalation_contacts: List[ContactInfo] = Field(default_factory=list, description="Contacts list to notify on escalation.")
    prompt_version: str = Field(...)
    provider: str = Field(...)
    model: str = Field(...)
    token_usage: TokenUsage = Field(...)
    latency_ms: float = Field(...)
