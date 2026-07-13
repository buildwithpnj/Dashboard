from typing import Dict, Any, List

class AgentHandoffService:
    @classmethod
    def create_handoff_frame(
        cls,
        sender: str,
        recipient: str,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a trace/state handoff frame.
        """
        return {
            "sender": sender,
            "recipient": recipient,
            "shared_state": state.copy(),
            "handoff_verified": True
        }

    @classmethod
    def verify_state_transition(
        cls,
        frame: Dict[str, Any],
        expected_keys: List[str]
    ) -> bool:
        """
        Validates that required keys exist in shared state.
        """
        state = frame.get("shared_state", {})
        for key in expected_keys:
            if key not in state:
                return False
        return True
