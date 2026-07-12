import pytest
from app.repositories.preview_events import PreviewEventsRepository
from app.services.preview_cost_tuner import PreviewCostTuner

def test_cost_efficiency_metrics():
    # Log mock events
    PreviewEventsRepository.log_event("sess123", "short prompt", "response", 100, 0.0001, "success")
    PreviewEventsRepository.log_event("sess123", "a long prompt to test cost efficiency calculations and grouping metrics in python script", "response", 200, 0.0002, "success")
    
    report = PreviewCostTuner.get_efficiency_report()
    assert "short" in report
    assert "medium" in report
    assert report["short"]["count"] == 1
    assert report["medium"]["count"] == 1
