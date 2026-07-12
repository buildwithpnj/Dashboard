from .preview_budget_service import PreviewBudgetService

class PreviewGuardrails:
    MAX_TURNS = 5
    MAX_TOKEN_BUDGET_SESSION = 2000
    MAX_TOKEN_BUDGET_DAILY = 50000

    @classmethod
    def check_limits(cls, session_id: str) -> str | None:
        """Returns error reason if limits exceeded, else None."""
        stats = PreviewBudgetService.get_session_stats(session_id)
        
        # Turn limits checks
        if stats["turns"] >= cls.MAX_TURNS:
            return f"Session turn limit of {cls.MAX_TURNS} exceeded. Please log in to continue."
            
        # Session token checks
        if stats["tokens"] >= cls.MAX_TOKEN_BUDGET_SESSION:
            return "Session token budget exceeded. Please start a new session or log in."

        # Daily token checks
        daily_tokens = PreviewBudgetService.get_daily_tokens()
        if daily_tokens >= cls.MAX_TOKEN_BUDGET_DAILY:
            return "Global daily budget limit reached. Please try again tomorrow."

        return None
