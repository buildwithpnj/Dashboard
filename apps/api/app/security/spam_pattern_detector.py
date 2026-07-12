class SpamPatternDetector:
    @classmethod
    def is_spam(cls, message: str) -> bool:
        cleaned = message.strip()
        if not cleaned:
            return True

        # 1. Repetitive characters check (e.g. "aaaaaaa...")
        if len(cleaned) > 10:
            char_set = set(cleaned)
            if len(char_set) <= 2:
                return True

        # 2. Meaningless word loop repetition checks
        words = cleaned.lower().split()
        if len(words) > 8:
            unique_words = set(words)
            # If unique words are less than 25% of total words, flag as spam loop
            if len(unique_words) / len(words) < 0.25:
                return True

        return False
