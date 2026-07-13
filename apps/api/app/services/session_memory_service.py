from typing import Dict, Any, Optional

class SessionMemoryService:
    # Memory-based session preference store to capture quick, ephemeral user instructions
    _session_store: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def set_session_preference(cls, session_id: str, key: str, value: Any) -> None:
        """
        Sets a key-value preference for the active chat session.
        """
        if session_id not in cls._session_store:
            cls._session_store[session_id] = {}
        cls._session_store[session_id][key] = value

    @classmethod
    def get_session_preference(cls, session_id: str, key: str) -> Optional[Any]:
        """
        Retrieves a session preference by key.
        """
        return cls._session_store.get(session_id, {}).get(key)

    @classmethod
    def get_all_session_preferences(cls, session_id: str) -> Dict[str, Any]:
        """
        Returns all accumulated session preferences.
        """
        return cls._session_store.get(session_id, {})

    @classmethod
    def clear_session(cls, session_id: str) -> None:
        """
        Evicts all preferences for a session.
        """
        cls._session_store.pop(session_id, None)
