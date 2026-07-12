"""
Translation Scorer for V8 Warborn Platform.

Evaluates translation quality with special handling for Hindi→English
workflows, including Devanagari script detection and Hinglish ambiguity.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Common romanized Hindi words that signal untranslated Hinglish leakage
_HINGLISH_MARKERS = {
    "accha", "arre", "bas", "bilkul", "bohot", "chalo", "dost",
    "haan", "hai", "kaise", "kya", "lekin", "matlab", "nahi",
    "nahin", "paisa", "paise", "phir", "sab", "theek", "thik",
    "wala", "yaar", "yeh",
}


class TranslationScorer:
    """Scores translation tasks, optimised for Hindi↔English pairs.

    Evaluates model translations across four dimensions:
    - semantic_preservation: meaning overlap with the reference
    - naturalness: penalises residual Devanagari in English output
    - script_handling: whether the output uses the correct script
    - hinglish_ambiguity: detects untranslated romanized Hindi words
    """

    def score(
        self,
        source_text: str,
        model_output: str,
        reference_text: str,
        source_lang: str = "hi",
        target_lang: str = "en",
    ) -> dict:
        """Score a translation task output.

        Args:
            source_text: The original text in the source language.
            model_output: The model's translated output.
            reference_text: The reference (gold) translation.
            source_lang: ISO 639-1 code for the source language.
            target_lang: ISO 639-1 code for the target language.

        Returns:
            Dict with semantic_preservation, naturalness,
            script_handling, and hinglish_ambiguity scores (0.0–1.0).
        """
        # --- semantic_preservation: word-level Jaccard with reference ---
        semantic_preservation = self._jaccard(model_output, reference_text)

        # --- naturalness: penalize residual Devanagari in English output ---
        if target_lang == "en":
            devanagari_chars = len(
                re.findall(r"[\u0900-\u097F]", model_output)
            )
            total_chars = max(len(model_output), 1)
            devanagari_ratio = devanagari_chars / total_chars
            naturalness = round(max(0.0, 1.0 - devanagari_ratio * 5.0), 4)
        else:
            naturalness = 1.0

        # --- script_handling ---
        if target_lang == "en":
            # Good if mostly ASCII/Latin; penalize Devanagari presence
            ascii_chars = sum(1 for c in model_output if ord(c) < 128)
            total = max(len(model_output), 1)
            script_handling = round(ascii_chars / total, 4)
        elif target_lang == "hi":
            # Good if Devanagari dominates
            devanagari = len(re.findall(r"[\u0900-\u097F]", model_output))
            total = max(len(model_output.replace(" ", "")), 1)
            script_handling = round(devanagari / total, 4)
        else:
            script_handling = 1.0

        # --- hinglish_ambiguity: detect romanized Hindi in English output ---
        if target_lang == "en":
            output_words = set(
                re.findall(r"[a-zA-Z]+", model_output.lower())
            )
            hinglish_hits = output_words & _HINGLISH_MARKERS
            if output_words:
                hit_ratio = len(hinglish_hits) / len(output_words)
                hinglish_ambiguity = round(max(0.0, 1.0 - hit_ratio * 5.0), 4)
            else:
                hinglish_ambiguity = 1.0
            if hinglish_hits:
                logger.debug(
                    "Hinglish markers detected: %s", hinglish_hits
                )
        else:
            hinglish_ambiguity = 1.0

        scores = {
            "semantic_preservation": round(semantic_preservation, 4),
            "naturalness": naturalness,
            "script_handling": script_handling,
            "hinglish_ambiguity": hinglish_ambiguity,
        }
        logger.info("TranslationScorer scores: %s", scores)
        return scores

    @staticmethod
    def _jaccard(s1: str, s2: str) -> float:
        """Word-level Jaccard similarity between two strings.

        Args:
            s1: First string.
            s2: Second string.

        Returns:
            Jaccard coefficient (0.0–1.0).
        """
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        return len(set1 & set2) / len(set1 | set2)
