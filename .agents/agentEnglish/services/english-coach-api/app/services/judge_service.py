import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class JudgeService:
    """Adjudicates close-score disputes, low-confidence cases, and gold-promotion reviews."""

    def __init__(self, model_name: str = 'gpt-4o'):
        self.model_name = model_name

    def adjudicate(
        self,
        input_text: str,
        model_output: str,
        reference_text: str,
        current_score: float,
        task_type: str
    ) -> Dict[str, Any]:
        """Runs adjudication over a candidate correction or translation to resolve score disputes."""
        logger.info(f"Adjudicating task_type={task_type} with score={current_score}")
        
        # Simple rule-based mock logic for test environment reliability
        if current_score >= 0.7:
            verdict = "approve"
            adjusted_score = max(current_score, 0.85)
            reason = "Preserves semantic meaning with correct syntax structure."
        elif current_score < 0.4:
            verdict = "reject"
            adjusted_score = min(current_score, 0.3)
            reason = "Significant syntactic errors or meaning mismatch."
        else:
            verdict = "uncertain"
            adjusted_score = current_score
            reason = "Minor ambiguity in naturalness or wording style choice."

        return {
            "verdict": verdict,
            "confidence": 0.90 if verdict != "uncertain" else 0.50,
            "reason": reason,
            "adjusted_score": adjusted_score,
            "model_used": self.model_name
        }

    def needs_adjudication(self, composite_score: float, score_dimensions: Dict[str, float]) -> bool:
        """Determines if an example falls within the disputed or low-confidence boundary."""
        # 1. Composite score in the ambiguous zone [0.4, 0.85]
        if 0.4 <= composite_score <= 0.85:
            return True
            
        # 2. Any individual dimension score is very low (< 0.3)
        if any(val < 0.3 for val in score_dimensions.values()):
            return True

        # 3. Variance of dimension scores is high (> 0.15)
        if score_dimensions:
            vals = list(score_dimensions.values())
            mean = sum(vals) / len(vals)
            variance = sum((x - mean) ** 2 for x in vals) / len(vals)
            if variance > 0.15:
                return True

        return False
