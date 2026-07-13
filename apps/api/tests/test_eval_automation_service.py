import pytest
import os
from app.services.eval_automation_service import EvalAutomationService

def test_run_eval_suite():
    # Make a temporary eval json
    temp_json = "temp_eval_set.json"
    import json
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump({
            "test_cases": [
                {"id": "T1", "expected_success": True},
                {"id": "T2", "expected_success": False}
            ]
        }, f)

    try:
        execution_results = [
            {"id": "T1", "success": True},
            {"id": "T2", "success": False}
        ]
        
        report = EvalAutomationService.run_eval_suite(temp_json, execution_results)
        assert report["total_cases"] == 2
        assert report["passed_cases"] == 2
        assert report["accuracy_percentage"] == 100.0
    finally:
        if os.path.exists(temp_json):
            os.remove(temp_json)
