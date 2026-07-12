from typing import Dict
from app.core.config import settings

class ModelRouter:
    """Config-driven router resolving active provider models based on product criticality constraints."""

    # Default model mappings optimized for cost and safety trade-offs
    PRODUCT_MODEL_MAPPING: Dict[str, str] = {
        "english_coach": "gpt-4o-mini",
        "lifeos_coach": "gpt-3.5-turbo",  # Cheaper model fallback for general wellness advice
        "family_checkin": "gpt-4o"       # Premium model for safety-critical parent monitoring
    }

    @classmethod
    def resolve_model(cls, product_id: str) -> str:
        """Resolves active LLM model key, matching fallbacks and cost profiles."""
        return cls.PRODUCT_MODEL_MAPPING.get(product_id, settings.MODEL_NAME)
