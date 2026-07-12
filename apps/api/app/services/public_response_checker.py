class PublicResponseChecker:
    @classmethod
    def check_response(cls, text: str) -> bool:
        """Returns True if response is safe and valid, else False."""
        cleaned = text.strip().lower()
        
        # 1. Length checks
        if len(text) > 1200:
            return False
            
        # 2. Block lists / unsafe patterns
        unsafe_words = ["system prompt", "openai", "apikey", "password", "hack", "bypass", "sql injection"]
        if any(w in cleaned for w in unsafe_words):
            return False
            
        # 3. Simple repetition check
        words = cleaned.split()
        if len(words) > 10:
            # Check if one word repeats more than 30% of the time
            word_counts: dict[str, int] = {}
            for w in words:
                word_counts[w] = word_counts.get(w, 0) + 1
            most_common = max(word_counts.values())
            if most_common / len(words) > 0.4:
                return False
                
        return True
