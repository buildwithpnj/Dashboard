class JailbreakDetector:
    # Set of common jailbreak patterns, system prompt bypass keywords, and key extraction triggers
    JAILBREAK_PATTERNS = [
        "ignore previous instructions",
        "system prompt",
        "you are now an unrestricted",
        "new rules",
        "do anything now",
        "dan mode",
        "hypothetical scenario where you",
        "bypass safeguards",
        "reveal your developer credentials",
        "extract api keys"
    ]

    @classmethod
    def is_jailbreak(cls, message: str) -> bool:
        cleaned = message.lower().strip()
        for pattern in cls.JAILBREAK_PATTERNS:
            if pattern in cleaned:
                return True
        return False
