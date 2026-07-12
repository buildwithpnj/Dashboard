from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class EvalCase(BaseModel):
    """Represents a single evaluation test case."""
    id: str = Field(..., description="Unique case identifier.")
    input_text: str = Field(..., description="The query input to coach.")
    expected_style: str = Field(..., description="Expected style class: hindi | hinglish | english | mixed | unknown.")
    expected_intent: str = Field(..., description="Expected intent class: translate | correct | rewrite_casual | rewrite_professional | explain.")
    expected_ambiguity: bool = Field(..., description="Expected ambiguity state flag.")
    reference_natural: Optional[str] = Field(None, description="Expected natural variant result comparison reference.")
    reference_professional: Optional[str] = Field(None, description="Expected professional variant result comparison reference.")
    tags: List[str] = Field(default_factory=list, description="Descriptive tag flags.")

class EvalResult(BaseModel):
    """Represents the results of running an evaluation case."""
    case_id: str = Field(..., description="Case identifier under check.")
    input_text: str = Field(..., description="The coached query.")
    detected_style: str = Field(..., description="Coached style return.")
    detected_intent: str = Field(..., description="Coached intent return.")
    actual_ambiguity: bool = Field(..., description="Coached ambiguity return.")
    natural_english: Optional[str] = Field(None, description="Coached natural translation.")
    professional_english: Optional[str] = Field(None, description="Coached professional rewrite.")
    explanation: Optional[str] = Field(None, description="Coached explanation text.")
    scores: Dict[str, float] = Field(..., description="Linguistic score breakdown scores (0.0 to 1.0).")
    weighted_score: float = Field(..., description="Aggregate scoring weighted index.")
    passed: bool = Field(..., description="Whether aggregate score is equal to or higher than threshold limit.")

class EvalSummary(BaseModel):
    """Represents the summary report of an evaluation run."""
    total_cases: int = Field(..., description="Total runs counted.")
    passed_cases: int = Field(..., description="Total passing runs counted.")
    failed_cases: int = Field(..., description="Total failing runs counted.")
    pass_rate: float = Field(..., description="Passing rate ratio percentage.")
    average_weighted_score: float = Field(..., description="Mean aggregate weighted scoring rate.")
    dimension_averages: Dict[str, float] = Field(..., description="Mean score rate per check dimension.")
    run_timestamp: str = Field(..., description="Execution completion timestamp.")

class ApprovedExample(BaseModel):
    """Represents a validated language pair context stored for retrieval injection."""
    id: str = Field(..., description="Unique example identification.")
    input_text: str = Field(..., description="Coached input sentence.")
    natural_english: str = Field(..., description="Approved conversational standard English version.")
    professional_english: str = Field(..., description="Approved formal standard English version.")
    tags: List[str] = Field(default_factory=list, description="Linguistic match tags.")
    created_at: str = Field(..., description="Creation ISO timestamp.")
