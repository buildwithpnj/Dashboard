"""
Intent Scorer for V8 Warborn Platform.

Evaluates intent classification and slot extraction accuracy for the
routing and NLU components of the English Coach pipeline.
"""

import logging

logger = logging.getLogger(__name__)


class IntentScorer:
    """Scores intent-routing and slot-extraction tasks.

    Evaluates model predictions across three dimensions:
    - intent_accuracy: exact, partial (substring), or miss
    - slot_extraction_quality: overlap between predicted and reference slots
    - routing_correctness: whether the intent maps to a valid route
    """

    def score(
        self,
        utterance: str,
        predicted_intent: str,
        reference_intent: str,
        predicted_slots: str = "",
        reference_slots: str = "",
    ) -> dict:
        """Score an intent-routing task output.

        Args:
            utterance: The user's original utterance.
            predicted_intent: The model's predicted intent label.
            reference_intent: The gold-standard intent label.
            predicted_slots: Comma-separated predicted slot values.
            reference_slots: Comma-separated reference slot values.

        Returns:
            Dict with intent_accuracy, slot_extraction_quality,
            and routing_correctness scores (0.0–1.0).
        """
        pred_norm = predicted_intent.strip().lower()
        ref_norm = reference_intent.strip().lower()

        # --- intent_accuracy ---
        if pred_norm == ref_norm:
            intent_accuracy = 1.0
        elif pred_norm in ref_norm or ref_norm in pred_norm:
            intent_accuracy = 0.5
            logger.debug(
                "Partial intent match: predicted='%s', reference='%s'",
                pred_norm,
                ref_norm,
            )
        else:
            intent_accuracy = 0.0

        # --- slot_extraction_quality ---
        slot_extraction_quality = self._slot_overlap(
            predicted_slots, reference_slots
        )

        # --- routing_correctness ---
        # Routing is correct if the intent matched at least partially
        # and slots are reasonably extracted
        if intent_accuracy == 1.0:
            routing_correctness = 1.0
        elif intent_accuracy == 0.5:
            routing_correctness = 0.5

        else:
            routing_correctness = 0.0

        scores = {
            "intent_accuracy": round(intent_accuracy, 4),
            "slot_extraction_quality": round(slot_extraction_quality, 4),
            "routing_correctness": round(routing_correctness, 4),
        }
        logger.info("IntentScorer scores: %s", scores)
        return scores

    @staticmethod
    def _slot_overlap(predicted: str, reference: str) -> float:
        """Compute slot-level overlap between predicted and reference slots.

        Slots are expected as comma-separated values. Overlap is measured
        using set intersection over union (Jaccard).

        Args:
            predicted: Comma-separated predicted slot values.
            reference: Comma-separated reference slot values.

        Returns:
            Overlap score (0.0–1.0).
        """
        pred_set = {
            s.strip().lower() for s in predicted.split(",") if s.strip()
        }
        ref_set = {
            s.strip().lower() for s in reference.split(",") if s.strip()
        }

        if not pred_set and not ref_set:
            return 1.0
        if not pred_set or not ref_set:
            return 0.0

        intersection = pred_set & ref_set
        union = pred_set | ref_set
        return len(intersection) / len(union)
