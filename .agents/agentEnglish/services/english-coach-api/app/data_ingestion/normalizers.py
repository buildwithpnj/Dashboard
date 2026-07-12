import re

class TextNormalizer:
    """Cleans raw string encodings and normalizes structural indentation spacing."""

    @staticmethod
    def normalize(text: str) -> str:
        """Collapses duplicate line endings and removes multi-space tabs."""
        if not text:
            return ""
        # Normalize double spacing and standard line endings
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()
