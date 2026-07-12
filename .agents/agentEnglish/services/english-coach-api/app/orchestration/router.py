class OrchestrationRouter:
    """Intent-based router parsing queries and dispatching execution flows to target agents."""

    def route_request(self, text: str) -> str:
        """Determines target product engine using simple semantic heuristics.
        
        Outputs:
            Target product key: english_coach | lifeos_coach | family_checkin
        """
        text_lower = text.lower()

        # LifeOS Health trigger checks
        health_triggers = {"calories", "steps", "sleep", "slept", "workout", "diet", "healthy", "exercise", "walked", "health"}
        if any(trigger in text_lower for trigger in health_triggers):
            return "lifeos_coach"

        # Family checkin triggers
        family_triggers = {"parent", "mom", "dad", "checkin", "check-in", "family", "elderly", "mother", "father", "wellness", "check in"}
        if any(trigger in text_lower for trigger in family_triggers) or "theek" in text_lower:
            return "family_checkin"

        # Default fallback
        return "english_coach"
