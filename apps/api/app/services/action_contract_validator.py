from typing import Dict, Any, Tuple

class ActionContractValidator:
    @classmethod
    def validate_create_contract(cls, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates payload structure and fields types.
        """
        if not isinstance(payload, dict):
            return False, "Payload must be a dictionary object."

        if "title" not in payload:
            return False, "Missing required key: 'title'"

        if not isinstance(payload["title"], str):
            return False, "Field 'title' must be a string."

        if "description" in payload and payload["description"] is not None:
            if not isinstance(payload["description"], str):
                return False, "Field 'description' must be a string."

        if "category" in payload and payload["category"] is not None:
            if not isinstance(payload["category"], str):
                return False, "Field 'category' must be a string."

        return True, "Contract check passed"
