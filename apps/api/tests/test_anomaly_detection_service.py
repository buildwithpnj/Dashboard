import pytest
from app.services.anomaly_detection_service import AnomalyDetectionService

def test_detect_loop_anomalies():
    # Regular run
    traces = [
        "Handoff to Retrieval: Context and profile loaded successfully.",
        "Handoff to Action: Executed create_task."
    ]
    report = AnomalyDetectionService.detect_loop_anomalies(traces)
    assert report["anomalies_detected"] is False

    # Loop anomaly run
    looping_traces = [
        "Handoff to Retrieval: Context and profile loaded successfully.",
        "Handoff to Retrieval: Context and profile loaded successfully.",
        "Handoff to Retrieval: Context and profile loaded successfully."
    ]
    report_loop = AnomalyDetectionService.detect_loop_anomalies(looping_traces)
    assert report_loop["anomalies_detected"] is True
    assert len(report_loop["flagged_repeats"]) == 1
    assert report_loop["severity"] == "WARNING"
