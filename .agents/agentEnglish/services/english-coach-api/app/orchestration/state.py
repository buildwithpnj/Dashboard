from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class OrchestrationState(BaseModel):
    """Tracks current workflow state, active agent, variables, and messages history."""
    session_id: str = Field(..., description="Active session key.")
    user_id: str = Field(..., description="Active user key.")
    product_id: str = Field(..., description="Currently selected routing target agent product.")
    history: List[Dict[str, str]] = Field(default_factory=list, description="Chronological role/content lists.")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Generic metadata variables.")
