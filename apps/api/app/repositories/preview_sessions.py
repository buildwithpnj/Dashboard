import uuid
from typing import Dict, Any, Optional

class PreviewSessionsRepository:
    _sessions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def create_session(cls, ip_address: str) -> str:
        session_id = str(uuid.uuid4())
        cls._sessions[session_id] = {
            "session_id": session_id,
            "ip_address": ip_address,
            "active": True
        }
        return session_id

    @classmethod
    def get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        return cls._sessions.get(session_id)
