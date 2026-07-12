from typing import Dict, Any

def enforce_coaching_policies(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validates and cleans coaching response properties.
    
    Ensures that non-ambiguous responses always have explanation comments.
    """
    if not response_data.get("ambiguity"):
        if not response_data.get("explanation"):
            response_data["explanation"] = "Sentence is grammatically correct and natural."
            
    return response_data
