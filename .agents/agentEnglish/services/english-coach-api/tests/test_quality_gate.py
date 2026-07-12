import pytest
from app.services.critic_service import CriticService
from app.services.quality_gate import QualityGate

@pytest.mark.anyio
async def test_critic_service_instruction_leak():
    """Verifies that the critic flags prompt instruction leakage inside generated text."""
    critic = CriticService()

    # 1. Valid output properties
    res_valid = {"natural_english": "Corrected sentence.", "explanation": "Refined."}
    eval_res = await critic.evaluate_output("input text", res_valid)
    assert eval_res["is_valid"] is True
    assert eval_res["quality_score"] == 1.0

    # 2. Leaked instruction payload
    res_leaked = {"natural_english": "SYSTEM PROMPT leak", "explanation": "leakage"}
    eval_res_leak = await critic.evaluate_output("input text", res_leaked)
    assert eval_res_leak["is_valid"] is False
    assert len(eval_res_leak["issues"]) > 0
    assert eval_res_leak["quality_score"] == 0.40

@pytest.mark.anyio
async def test_quality_gate_repair():
    """Verifies that the quality gate successfully triggers repair callables on invalid data."""
    critic = CriticService()
    gate = QualityGate(critic)

    # Mock repair function returning valid structure
    async def mock_repair_callable():
        return {"natural_english": "Corrected repaired output.", "explanation": "repaired"}

    invalid_data = {"natural_english": "SYSTEM PROMPT leak", "explanation": "leakage"}

    # Repair should trigger and yield corrected output
    repaired = await gate.validate_and_repair("input", invalid_data, mock_repair_callable)
    assert repaired["natural_english"] == "Corrected repaired output."
