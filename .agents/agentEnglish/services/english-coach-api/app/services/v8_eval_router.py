import logging
from typing import Optional

logger = logging.getLogger(__name__)


class V8EvalRouter:
    """Routes normalized eval examples to the appropriate task-specific scorer.
    
    Maps task_type values to scorer classes:
    - correction  → CorrectionScorer
    - translation → TranslationScorer
    - intent_routing → IntentScorer
    """

    def __init__(self):
        # Lazy-load scorers to avoid circular imports
        self._scorers = {}

    def _get_scorer(self, task_type: str):
        """Returns the appropriate scorer instance for a task type."""
        if task_type not in self._scorers:
            if task_type == "correction":
                from app.services.scoring.correction_scorer import CorrectionScorer
                self._scorers[task_type] = CorrectionScorer()
            elif task_type == "translation":
                from app.services.scoring.translation_scorer import TranslationScorer
                self._scorers[task_type] = TranslationScorer()
            elif task_type == "intent_routing":
                from app.services.scoring.intent_scorer import IntentScorer
                self._scorers[task_type] = IntentScorer()
            else:
                logger.warning(f"No scorer registered for task_type='{task_type}'. Returning empty scores.")
                return None
        return self._scorers[task_type]

    def score_example(self, example: dict, model_output: str) -> dict:
        """Scores a single eval example using the appropriate task-specific scorer.
        
        Args:
            example: Normalized eval example dict with task_type and reference fields.
            model_output: The model's generated output to score.
            
        Returns:
            Dict of per-dimension scores (0.0 to 1.0) or empty dict if no scorer found.
        """
        task_type = example.get("task_type", "")
        scorer = self._get_scorer(task_type)
        if scorer is None:
            return {}

        if task_type == "correction":
            return scorer.score(
                input_text=example.get("source_text", ""),
                model_output=model_output,
                reference_corrections=example.get("reference_corrections", [])
            )
        elif task_type == "translation":
            return scorer.score(
                source_text=example.get("source_text", ""),
                model_output=model_output,
                reference_text=example.get("target_text", ""),
                source_lang=example.get("source_lang", "hi"),
                target_lang=example.get("target_lang", "en")
            )
        elif task_type == "intent_routing":
            return scorer.score(
                utterance=example.get("utterance", ""),
                predicted_intent=model_output,
                reference_intent=example.get("intent", ""),
                predicted_slots="",
                reference_slots=example.get("slots", "")
            )
        return {}

    def score_with_safety(self, example: dict, model_output: str, product_id: str = "english_coach") -> dict:
        """Scores an example with both task-specific and safety scoring.
        
        Returns combined dimension scores including safety dimensions.
        """
        task_scores = self.score_example(example, model_output)

        # Add safety scoring
        from app.services.scoring.safety_scorer import SafetyScorer
        safety_scorer = SafetyScorer()
        input_text = example.get("source_text", example.get("utterance", ""))
        safety_scores = safety_scorer.score(
            input_text=input_text,
            model_output=model_output,
            task_type=example.get("task_type", ""),
            product_id=product_id
        )

        # Merge all dimensions
        combined = {**task_scores, **safety_scores}
        return combined
