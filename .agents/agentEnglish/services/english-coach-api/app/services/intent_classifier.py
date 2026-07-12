class IntentClassifier:
    """Classifies input task intents: translate, correct, rewrite_casual, rewrite_professional, or explain."""

    def classify(self, text: str) -> str:
        """Heuristically classifies the task intent from the input text."""
        text_lower = text.lower()
        
        if "rewrite" in text_lower or "casual" in text_lower:
            if "professional" in text_lower or "formal" in text_lower:
                return "rewrite_professional"
            return "rewrite_casual"
            
        if "professional" in text_lower or "formal" in text_lower or "corporate" in text_lower:
            return "rewrite_professional"
            
        if "explain" in text_lower or "mistake" in text_lower or "why" in text_lower:
            return "explain"
            
        if any(marker in text_lower for marker in ["translate", "hindi", "hinglish", "meaning", "matlab"]):
            return "translate"
            
        return "correct"
