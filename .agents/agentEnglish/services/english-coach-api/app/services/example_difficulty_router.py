import logging
import re
from app.core.config import settings

logger = logging.getLogger(__name__)

class ExampleDifficultyRouter:
    """Classifies evaluation examples into difficulty tiers and routes to appropriate models."""

    def __init__(self, premium_cap_pct: int = 5):
        self.premium_cap_pct = premium_cap_pct

    def classify_difficulty(self, example: dict) -> str:
        """Classifies example difficulty based on characters length, multi-reference, and script mixes."""
        input_text = example.get("source_text", example.get("utterance", ""))
        task_type = example.get("task_type", "")
        
        # 1. Easy: short utterances, intent routing
        if len(input_text) < 50 and task_type == "intent_routing":
            return "easy"

        # 2. Hard: long text (>200 chars), script mixing, or multiple reference corrections
        has_devanagari = bool(re.search(r"[\u0900-\u097F]", input_text))
        has_latin = bool(re.search(r"[a-zA-Z]", input_text))
        script_mixing = has_devanagari and has_latin

        refs = example.get("reference_corrections", [])
        multiple_refs = len(refs) > 1

        if len(input_text) > 200 or script_mixing or multiple_refs:
            return "hard"

        # 3. Medium: Standard cases
        return "medium"

    def route_to_model(self, difficulty: str, tier_counts: dict, total_count: int) -> str:
        """Routes task difficulty to appropriate cheap, standard or premium model tier within percent caps."""
        if difficulty == "easy":
            return settings.CHEAP_MODEL_NAME

        if difficulty == "hard":
            premium_count = tier_counts.get("premium", 0)
            # Enforce percentage cap constraint
            if total_count > 0 and (premium_count / total_count * 100.0) >= self.premium_cap_pct:
                logger.warning("Premium model tier cap reached. Routing hard example to standard model instead.")
                return settings.MODEL_NAME
            return settings.PREMIUM_MODEL_NAME

        return settings.MODEL_NAME
