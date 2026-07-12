from typing import Dict, Any, List, Optional

class ActionRegistry:
    # Centrally defined dictionary of safe tools metadata and schemas
    ACTIONS = {
        "save_corrected_example": {
            "description": "Saves a corrected sentence and its explanation to the user library.",
            "allowed_roles": ["approved_user", "internal_admin"],
            "requires_approval": False,
            "input_schema": {
                "original": str,
                "corrected": str,
                "explanation": str
            }
        },
        "create_lesson_note": {
            "description": "Saves a learning or lesson note card from the conversation.",
            "allowed_roles": ["approved_user", "internal_admin"],
            "requires_approval": False,
            "input_schema": {
                "title": str,
                "content": str
            }
        },
        "update_preference": {
            "description": "Updates tone, explanation style, target level, or language support preferences.",
            "allowed_roles": ["approved_user", "internal_admin"],
            "requires_approval": False,
            "input_schema": {
                "tone": str,
                "explanation_style": str
            }
        },
        "mark_pattern_mastered": {
            "description": "Marks a specific grammar or correction pattern as mastered.",
            "allowed_roles": ["approved_user", "internal_admin"],
            "requires_approval": False,
            "input_schema": {
                "pattern_name": str
            }
        },
        "create_followup_practice": {
            "description": "Generates and logs a practice task reminder for later.",
            "allowed_roles": ["approved_user", "internal_admin"],
            "requires_approval": True,  # Higher-risk reminder tasks require user approval
            "input_schema": {
                "task_description": str
            }
        }
    }

    @classmethod
    def get_action(cls, action_name: str) -> Optional[Dict[str, Any]]:
        return cls.ACTIONS.get(action_name)

    @classmethod
    def list_actions(cls) -> List[str]:
        return list(cls.ACTIONS.keys())

    @classmethod
    def validate_inputs(cls, action_name: str, payload: Dict[str, Any]) -> bool:
        action = cls.get_action(action_name)
        if not action:
            return False
            
        schema = action["input_schema"]
        for key, expected_type in schema.items():
            if key not in payload:
                return False
            if not isinstance(payload[key], expected_type):
                return False
        return True
