from typing import Dict, Any

def enforce_family_escalation_policy(text: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Checks parent replies for severe distress signs (e.g. falls, chest pains, accidents).
    
    If keywords trigger, forces checkin_status to 'escalated' and flags escalation_triggered=True.
    """
    distress_keywords = {
        "chest", "pain", "hurt", "fell", "gira", "chhati", "dard", "hospital",
        "accident", "emergency", "marna", "die", "ambulance", "blood", "khun", "chot"
    }

    words = {w.strip(".,?!;:()\"'") for w in text.lower().split() if w.strip()}
    triggered = len(words.intersection(distress_keywords)) > 0

    if triggered or response_data.get("escalation_triggered", False):
        response_data["escalation_triggered"] = True
        response_data["checkin_status"] = "escalated"
        response_data["notes"] = f"EMERGENCY ESCALATION ALERT: Distress words detected. {response_data.get('notes', '')}".strip()

    return response_data
