from typing import Dict, Any

class CriticService:
    """Validates generated assistant responses for instruction leaks, content alignment, and structure."""

    async def evaluate_output(self, user_input: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs quality validations returning safety and compliance status metrics.
        
        Checks for:
            - Stable instructions leakage (system instructions printed in public fields).
            - Empty translation outputs for non-ambiguous cases.
        """
        issues = []
        is_valid = True

        # Check for system template leakages
        system_leaks = {"system instruction", "output schema", "behaviours rule", "stable instructions", "pydantic", "system prompt"}
        for key in ["natural_english", "professional_english", "explanation", "response_text"]:
            val = response_data.get(key)
            if val and isinstance(val, str):
                val_lower = val.lower()
                if any(leak in val_lower for leak in system_leaks):
                    issues.append(f"Prompt instruction leak detected in field '{key}'.")
                    is_valid = False

        # Confirm non-ambiguous English Coach outputs actually contain text
        if not response_data.get("ambiguity", False) and "natural_english" in response_data:
            if not response_data.get("natural_english"):
                issues.append("Missing required 'natural_english' translation output.")
                is_valid = False

        return {
            "is_valid": is_valid,
            "issues": issues,
            "quality_score": 1.0 if is_valid else 0.40
        }
