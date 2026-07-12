import re

def clean_text(text: str) -> str:
    """Standardizes spaces and strips leading/trailing whitespaces in text inputs."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def validate_input_text(text: str) -> str:
    """Validates that text is non-empty and contains actual characters.
    
    Raises:
        ValueError: If text is empty or only contains whitespace.
    """
    cleaned = clean_text(text)
    if not cleaned:
        raise ValueError("Input text cannot be empty or contain only whitespace.")
    return cleaned
