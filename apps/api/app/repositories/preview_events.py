from typing import List, Dict, Any

class PreviewEventsRepository:
    _events: List[Dict[str, Any]] = []

    @classmethod
    def log_event(
        cls, 
        session_id: str, 
        prompt: str, 
        response: str, 
        tokens: int, 
        cost: float, 
        status: str
    ):
        event = {
            "session_id": session_id,
            "prompt": prompt,
            "response": response,
            "tokens": tokens,
            "cost": cost,
            "status": status
        }
        cls._events.append(event)

    @classmethod
    def get_all_events(cls) -> List[Dict[str, Any]]:
        return cls._events
