"""
Correction Scorer for V8 Warborn Platform.

Evaluates grammar correction quality by comparing model output against
reference corrections using Jaccard similarity, fluency ratios, and
brevity controls.
"""

import logging

logger = logging.getLogger(__name__)


class CorrectionScorer:
    """Scores grammar/spelling correction tasks.

    Evaluates model corrections across four dimensions:
    - meaning_preservation: how well the corrected text preserves original meaning
    - grammar_quality: whether the correction actually improved grammar
    - fluency: how natural the output reads relative to references
    - brevity_control: penalizes excessively verbose corrections
    """

    def score(
        self,
        input_text: str,
        model_output: str,
        reference_corrections: list,
    ) -> dict:
        """Score a correction task output against references.

        Args:
            input_text: The original uncorrected text.
            model_output: The model's corrected output.
            reference_corrections: List of acceptable reference corrections.

        Returns:
            Dict with meaning_preservation, grammar_quality, fluency,
            and brevity_control scores, each in the range 0.0–1.0.
        """
        if not reference_corrections:
            logger.warning("No reference corrections provided; returning zeros.")
            return {
                "meaning_preservation": 0.0,
                "grammar_quality": 0.0,
                "fluency": 0.0,
                "brevity_control": 0.0,
            }

        # --- meaning_preservation: best Jaccard with any reference ---
        best_jaccard = 0.0
        best_ref = reference_corrections[0]
        for ref in reference_corrections:
            j = self._jaccard(model_output, ref)
            if j > best_jaccard:
                best_jaccard = j
                best_ref = ref
        meaning_preservation = round(best_jaccard, 4)

        # --- grammar_quality ---
        if model_output.strip().lower() == input_text.strip().lower():
            # Model made no change at all
            grammar_quality = 0.3
            logger.debug("Model output identical to input; grammar_quality=0.3")
        else:
            # Credit based on similarity to the best reference
            grammar_quality = round(min(best_jaccard * 1.2, 1.0), 4)

        # --- fluency: word-count ratio vs best reference ---
        output_words = len(model_output.split())
        ref_words = len(best_ref.split())
        if ref_words == 0:
            fluency = 0.0
        else:
            ratio = output_words / ref_words
            # Perfect ratio = 1.0 → fluency 1.0; divergence penalised
            fluency = round(max(0.0, 1.0 - abs(1.0 - ratio)), 4)

        # --- brevity_control: penalize if output >2x words of input ---
        input_words = len(input_text.split())
        if input_words == 0:
            brevity_control = 1.0
        else:
            word_ratio = output_words / input_words
            if word_ratio <= 2.0:
                brevity_control = 1.0
            else:
                # Linear decay beyond 2x
                brevity_control = round(max(0.0, 1.0 - (word_ratio - 2.0) / 2.0), 4)

        scores = {
            "meaning_preservation": meaning_preservation,
            "grammar_quality": grammar_quality,
            "fluency": fluency,
            "brevity_control": brevity_control,
        }
        logger.info("CorrectionScorer scores: %s", scores)
        return scores

    @staticmethod
    def _jaccard(s1: str, s2: str) -> float:
        """Compute Jaccard similarity between two strings (word-level).

        Args:
            s1: First string.
            s2: Second string.

        Returns:
            Jaccard similarity coefficient in the range 0.0–1.0.
        """
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union)
