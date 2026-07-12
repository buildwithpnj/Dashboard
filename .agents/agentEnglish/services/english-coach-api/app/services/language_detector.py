class LanguageDetector:
    """Classifies input text style: hindi, hinglish, english, mixed, or unknown."""

    def detect(self, text: str) -> str:
        """Determines the style of the input text using light heuristic rules."""
        if not text or not text.strip():
            return "unknown"
            
        text_lower = text.strip().lower()
        
        # Hindi Devnagari character range
        if any(ord(char) >= 2304 and ord(char) <= 2431 for char in text):
            return "hindi"

        # Common Hinglish phonetic words
        hinglish_markers = {
            "hai", "ko", "kya", "tha", "ho", "bhi", "aur", "se", "ek", "kar", 
            "rha", "raha", "gaya", "nhi", "nahi", "ya", "ki", "ka", "ke", "ne",
            "par", "hum", "main", "tum", "aap", "chal", "karo", "de", "do", "dena",
            "usko", "bol", "bhejna"
        }
        
        words = set(text_lower.split())
        matched_markers = words.intersection(hinglish_markers)
        
        if len(matched_markers) > 0:
            english_words = {"please", "rewrite", "professionally", "join", "because", "network", "client", "update", "issue", "i", "am", "not", "able", "to"}
            has_english = len(words.intersection(english_words)) > 0
            if has_english:
                return "mixed"
            return "hinglish"
            
        # If it doesn't match markers but consists of standard latin alphabets, default to english
        if any(char.isalpha() for char in text_lower):
            return "english"
            
        return "unknown"
