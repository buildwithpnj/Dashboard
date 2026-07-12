import pytest
from app.services.eval_cost_controller import EvalCostController

def test_cost_controller_budget_bounds():
    # Budget limit = $0.10
    controller = EvalCostController(budget_limit_usd=0.10)

    # 1. Under limit check
    check = controller.check_budget()
    assert check["allowed"] is True
    assert check["action"] == "continue"

    # 2. Trigger warning at 80% ($0.08)
    # Record usage of 9000 tokens on premium model (gpt-4o Blended blended rate ~0.015 / 1K tokens => 9 * 0.015 = 0.135 USD)
    # Let's directly record tokens to reach warning threshold.
    # Rate of premium is 0.015 per 1K. 6000 tokens = 6 * 0.015 = 0.09 USD.
    controller.record_usage("gpt-4o", 6000)
    
    check = controller.check_budget()
    assert check["allowed"] is True
    assert check["action"] == "downgrade" # Warning active
    assert check["utilization_pct"] >= 80.0

    # 3. Trigger hard stop at 100% ($0.10)
    controller.record_usage("gpt-4o", 2000) # Increments by 2 * 0.015 = 0.03 USD => total $0.12 USD
    check = controller.check_budget()
    assert check["allowed"] is False
    assert check["action"] == "stop"
