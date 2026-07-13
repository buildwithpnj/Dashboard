import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("memory_write_guard")

class MemoryWriteGuard:
    @classmethod
    def validate_memory_write(
        cls,
        updates: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validates memory update requests. Returns (is_valid, reason).
        Checks:
        1. Only allowed tones are stored.
        2. Field length boundaries are respected.
        3. Weaknesses and goals are structured lists.
        """
        # Tone boundaries validation
        allowed_tones = ["professional", "conversational", "concise"]
        if "tone" in updates:
            tone = updates["tone"]
            if tone not in allowed_tones:
                return False, f"Invalid tone '{tone}'. Allowed tones: {allowed_tones}"

        # Style boundaries validation
        allowed_styles = ["detailed", "brief", "rule-based"]
        if "explanation_style" in updates:
            style = updates["explanation_style"]
            if style not in allowed_styles:
                return False, f"Invalid explanation style '{style}'. Allowed styles: {allowed_styles}"

        # Weaknesses list validation
        if "weaknesses" in updates:
            weaknesses = updates["weaknesses"]
            if not isinstance(weaknesses, list):
                return False, "Weaknesses field must be a structured list."
            for item in weaknesses:
                if not isinstance(item, str) or len(item.strip()) == 0:
                    return False, "Individual weakness items must be non-empty strings."
                if len(item) > 100:
                    return False, "Individual weakness items must be under 100 characters."

        # Goals list validation
        if "goals" in updates:
            goals = updates["goals"]
            if not isinstance(goals, list):
                return False, "Goals field must be a structured list."
            for item in goals:
                if not isinstance(item, str) or len(item.strip()) == 0:
                    return False, "Individual goal items must be non-empty strings."
                if len(item) > 100:
                    return False, "Individual goal items must be under 100 characters."

        # Preferred language validation
        if "preferred_language" in updates:
            lang = updates["preferred_language"]
            if not isinstance(lang, str) or len(lang.strip()) == 0:
                return False, "Preferred language must be a non-empty string."
            if len(lang) > 50:
                return False, "Preferred language must be under 50 characters."

        return True, "Validation successful"
