from typing import Dict, Any

def enforce_medical_disclaimer_policy(text: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Inspects input text and parsed responses for medical terms.
    
    If keywords like 'pain', 'chest', or 'medicine' are present, it overrides
    the disclaimer_triggered state and prepends a medical disclaimer warning.
    """
    medical_keywords = {
        "pain", "chest", "headache", "fever", "disease", "drug", "medicine",
        "pill", "prescribe", "cancer", "diabetes", "sick", "cough", "symptom", "diagnose"
    }

    words = {w.strip(".,?!;:()\"'") for w in text.lower().split() if w.strip()}
    keyword_triggered = len(words.intersection(medical_keywords)) > 0

    if keyword_triggered or response_data.get("disclaimer_triggered", False):
        response_data["disclaimer_triggered"] = True
        disclaimer_text = "DISCLAIMER: This is a wellness check-in, not a medical diagnosis. Please consult a qualified doctor for any medical symptoms."
        
        # Prepend to analysis block if not already there
        current_analysis = response_data.get("analysis", "")
        if disclaimer_text not in current_analysis:
            response_data["analysis"] = f"{disclaimer_text}\n\n{current_analysis}".strip()

    return response_data
