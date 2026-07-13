import pytest
from app.services.agent_handoff_service import AgentHandoffService

def test_handoff_frame_verification():
    state = {"workspace_context": ["release goals"], "user_preferences": []}
    
    frame = AgentHandoffService.create_handoff_frame(
        sender="coordinator",
        recipient="retrieval",
        state=state
    )
    
    assert frame["sender"] == "coordinator"
    assert frame["recipient"] == "retrieval"
    assert frame["shared_state"]["workspace_context"] == ["release goals"]
    
    # Valid transition keys check
    assert AgentHandoffService.verify_state_transition(frame, ["workspace_context", "user_preferences"]) is True
    # Invalid transition keys check
    assert AgentHandoffService.verify_state_transition(frame, ["missing_key"]) is False
