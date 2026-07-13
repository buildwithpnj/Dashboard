from app.services.agent_analytics_service import AgentAnalyticsService
from typing import Dict, Any

class RuntimeHealthDashboardService:
    @classmethod
    def compile_health_summary(cls) -> Dict[str, Any]:
        """
        Compiles timings, status metrics, and health scores.
        """
        avg_lat = AgentAnalyticsService.get_average_latency()
        spike = AgentAnalyticsService.detect_latency_spike()
        
        health_score = 100
        if avg_lat > 1500.0:
            health_score -= 10
        if spike:
            health_score -= 15

        return {
            "health_score": max(health_score, 0),
            "average_latency_ms": round(avg_lat, 2),
            "latency_spike_detected": spike,
            "status": "HEALTHY" if health_score >= 80 else "DEGRADED"
        }
