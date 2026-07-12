class PreviewFallbackService:
    @classmethod
    def get_fallback(cls, trigger: str) -> str:
        """Returns clean premium client fallback copy based on trigger reason."""
        fallbacks = {
            "budget_exhausted": (
                "You have reached the preview limit. Please log in or request "
                "full developer credentials to access the unrestricted Warborn system."
            ),
            "timeout": (
                "The request timed out due to high system load. Please try again in a moment "
                "or access our dedicated low-latency authenticated system."
            ),
            "abuse_blocked": (
                "Your request triggered our safety rules. To protect the sandbox environment, "
                "this request has been blocked. Enter the secure dashboard for full model control."
            ),
            "cooldown": (
                "Your session has been temporarily rate limited due to rapid message pacing. "
                "Please wait 5 minutes before submitting your next prompt."
            ),
            "unsupported_intent": (
                "This preview only supports English correction, rephrasing, Hinglish translation, "
                "or grammar explanation. Please sign in to ask general developer questions."
            )
        }
        return fallbacks.get(trigger, "Service currently unavailable. Please sign in.")
