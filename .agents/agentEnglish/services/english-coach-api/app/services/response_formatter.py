import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Parses, validates, and normalizes JSON schemas returned from LLM provider completions."""

    def parse_llm_response(self, raw_response: str) -> Dict[str, Any]:
        """Strips markdown delimiters and parses the payload into a Python dictionary.
        
        Args:
            raw_response: Raw response string from provider.
            
        Returns:
            Decoded dictionary representing the coach response.
            
        Raises:
            ValueError: If parsing fails.
        """
        cleaned = raw_response.strip()
        
        # Remove potential markdown block wraps
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
            
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as decode_err:
            logger.error(f"Failed to decode provider response: {raw_response}. Err: {decode_err}")
            raise ValueError(f"Provider output is not valid JSON: {decode_err}")

    def normalize_response(self, parsed_data: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Ensures all expected keys conform to target data types and values."""
        normalized = {}
        
        # Style & intent fallbacks are handled at the service level, but we ensure string types here
        normalized["detected_input_style"] = str(parsed_data.get("detected_input_style", "English"))
        normalized["intent"] = str(parsed_data.get("intent", "correct"))
        
        # Output sentences (can be null/None)
        normalized["natural_english"] = parsed_data.get("natural_english")
        if normalized["natural_english"] is not None:
            normalized["natural_english"] = str(normalized["natural_english"])
            
        normalized["professional_english"] = parsed_data.get("professional_english")
        if normalized["professional_english"] is not None:
            normalized["professional_english"] = str(normalized["professional_english"])
            
        normalized["explanation"] = parsed_data.get("explanation")
        if normalized["explanation"] is not None:
            normalized["explanation"] = str(normalized["explanation"])
            
        # Ambiguity
        normalized["ambiguity"] = bool(parsed_data.get("ambiguity", False))
        
        normalized["clarification_question"] = parsed_data.get("clarification_question")
        if normalized["clarification_question"] is not None:
            normalized["clarification_question"] = str(normalized["clarification_question"])
            
        # Mistake tags list
        tags = parsed_data.get("mistake_tags", [])
        if not isinstance(tags, list):
            tags = []
        normalized["mistake_tags"] = [str(t) for t in tags]
        
        # Confidence score
        try:
            normalized["confidence"] = float(parsed_data.get("confidence", 0.90))
        except (ValueError, TypeError):
            normalized["confidence"] = 0.90
            
        return normalized
