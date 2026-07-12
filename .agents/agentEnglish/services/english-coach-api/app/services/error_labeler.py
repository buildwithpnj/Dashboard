import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class ErrorLabeler:
    """Labels evaluation failures into structured error buckets based on metrics."""

    BUCKETS = [
        "wrong_correction",
        "over_correction",
        "under_correction",
        "wrong_translation",
        "unnatural_translation",
        "wrong_intent",
        "weak_retrieval",
        "noisy_retrieval",
        "escalation_miss",
        "unsafe_answer",
        "too_verbose",
        "unnecessary_token_spend"
    ]

    def label(
        self,
        task_type: str,
        scores: Dict[str, float],
        input_text: str,
        model_output: str,
        tokens_used: int = 0
    ) -> Optional[str]:
        """Classifies response failure into specific bucket using dimension scores."""
        # 1. Unsafe advice detection
        if scores.get("unsafe_advice_detection", 1.0) < 0.5:
            return "unsafe_answer"

        # 2. Escalation failures
        if scores.get("escalation_correctness", 1.0) < 0.5:
            return "escalation_miss"

        # 3. Too verbose response check
        words_in = len(input_text.split())
        words_out = len(model_output.split())
        if words_in > 0 and words_out > (words_in * 3):
            return "too_verbose"

        # 4. Token cost / budget inefficiency
        if tokens_used > 500 and sum(scores.values()) / len(scores) < 0.5:
            return "unnecessary_token_spend"

        # 5. Task-specific routing labels
        if task_type == "correction":
            if scores.get("grammar_quality", 1.0) < 0.4:
                return "wrong_correction"
            if scores.get("meaning_preservation", 1.0) < 0.4:
                return "over_correction"
            if input_text.strip().lower() == model_output.strip().lower():
                return "under_correction"

        elif task_type == "translation":
            if scores.get("semantic_preservation", 1.0) < 0.4:
                return "wrong_translation"
            if scores.get("naturalness", 1.0) < 0.4:
                return "unnatural_translation"

        elif task_type == "intent_routing":
            if scores.get("intent_accuracy", 1.0) < 0.4:
                return "wrong_intent"

        # Check retrieval quality if logged in dimensions
        if scores.get("retrieval_relevance", 1.0) < 0.3:
            return "weak_retrieval"
        if scores.get("retrieval_noise", 1.0) < 0.3:
            return "noisy_retrieval"

        # Standard check: if aggregate score is low, default label
        avg_score = sum(scores.values()) / len(scores) if scores else 1.0
        if avg_score < 0.5:
            if task_type == "correction":
                return "wrong_correction"
            elif task_type == "translation":
                return "wrong_translation"
            elif task_type == "intent_routing":
                return "wrong_intent"

        return None

    def is_uncertain(self, label: Optional[str], composite_score: float) -> bool:
        """Flags cases needing manual label or judge review."""
        return label is None and (0.4 <= composite_score <= 0.7)
