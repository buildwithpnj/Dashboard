from typing import Dict, Any, List
from app.repositories.preview_events import PreviewEventsRepository
from app.services.preview_budget_service import PreviewBudgetService

class PreviewAnalyticsService:
    _landing_visits: int = 0
    _login_clicks: int = 0
    _request_access_clicks: int = 0

    @classmethod
    def increment_visit(cls):
        cls._landing_visits += 1

    @classmethod
    def increment_login_click(cls):
        cls._login_clicks += 1

    @classmethod
    def increment_request_access_click(cls):
        cls._request_access_clicks += 1

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        events = PreviewEventsRepository.get_all_events()
        total_turns = len(events)
        
        # Calculate totals
        total_tokens = sum(e["tokens"] for e in events)
        total_cost = sum(e["cost"] for e in events)
        blocked_attempts = sum(1 for e in events if e["status"] == "blocked")
        success_attempts = sum(1 for e in events if e["status"] == "success")
        
        # Unique sessions
        sessions = set(e["session_id"] for e in events)
        total_sessions = len(sessions)
        
        avg_turns = (total_turns / total_sessions) if total_sessions > 0 else 0.0
        avg_cost = (total_cost / total_sessions) if total_sessions > 0 else 0.0
        
        # Simple Conversion Metric: Clicks on login / total unique visits
        conversion_rate = (cls._login_clicks / cls._landing_visits * 100) if cls._landing_visits > 0 else 0.0

        return {
            "landing_page_visits": cls._landing_visits,
            "preview_starts": total_sessions,
            "preview_turns": total_turns,
            "blocked_abuse_attempts": blocked_attempts,
            "success_preview_responses": success_attempts,
            "average_turns_per_session": round(avg_turns, 2),
            "average_cost_per_session_usd": round(avg_cost, 6),
            "total_tokens_consumed": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "login_cta_clicks": cls._login_clicks,
            "request_access_clicks": cls._request_access_clicks,
            "conversion_rate_percentage": round(conversion_rate, 2)
        }
