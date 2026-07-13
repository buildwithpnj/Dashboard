import pytest
from app.services.agent_analytics_service import AgentAnalyticsService
from app.services.runtime_health_dashboard_service import RuntimeHealthDashboardService

def test_analytics_metrics():
    AgentAnalyticsService._latency_records.clear()
    
    AgentAnalyticsService.record_latency(100.0)
    AgentAnalyticsService.record_latency(300.0)
    
    assert AgentAnalyticsService.get_average_latency() == 200.0
    assert AgentAnalyticsService.detect_latency_spike(150.0) is True
    assert AgentAnalyticsService.detect_latency_spike(400.0) is False

def test_health_dashboard_compilation():
    AgentAnalyticsService._latency_records.clear()
    AgentAnalyticsService.record_latency(2200.0)
    
    summary = RuntimeHealthDashboardService.compile_health_summary()
    assert summary["health_score"] < 100
    assert summary["average_latency_ms"] == 2200.0
    assert summary["latency_spike_detected"] is True
    assert summary["status"] == "DEGRADED"
