from datetime import date
from typing import Dict, Any

class PreviewBudgetService:
    # In-memory database/cache tracking
    _sessions: Dict[str, Dict[str, Any]] = {}
    _daily_usage: Dict[str, int] = {}

    @classmethod
    def get_session_stats(cls, session_id: str) -> Dict[str, Any]:
        if session_id not in cls._sessions:
            cls._sessions[session_id] = {
                "turns": 0,
                "tokens": 0,
                "cost": 0.0
            }
        return cls._sessions[session_id]

    @classmethod
    def increment_session(cls, session_id: str, tokens: int, cost: float):
        stats = cls.get_session_stats(session_id)
        stats["turns"] += 1
        stats["tokens"] += tokens
        stats["cost"] += cost
        
        # Track daily usage
        today = str(date.today())
        cls._daily_usage[today] = cls._daily_usage.get(today, 0) + tokens

    @classmethod
    def get_daily_tokens(cls) -> int:
        today = str(date.today())
        return cls._daily_usage.get(today, 0)

    @classmethod
    def reset_daily_budget(cls):
        today = str(date.today())
        cls._daily_usage[today] = 0
