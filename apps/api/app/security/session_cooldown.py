import time
from typing import Dict

class SessionCooldown:
    # Track cooldown expiry time: session_id -> expiry_timestamp
    _cooldowns: Dict[str, float] = {}
    COOLDOWN_DURATION = 300.0  # 5 minutes block

    @classmethod
    def apply_cooldown(cls, session_id: str):
        cls._cooldowns[session_id] = time.time() + cls.COOLDOWN_DURATION

    @classmethod
    def is_cooling_down(cls, session_id: str) -> bool:
        if session_id in cls._cooldowns:
            expiry = cls._cooldowns[session_id]
            if time.time() < expiry:
                return True
            else:
                # Expired
                del cls._cooldowns[session_id]
        return False

    @classmethod
    def get_remaining_seconds(cls, session_id: str) -> int:
        if session_id in cls._cooldowns:
            remaining = cls._cooldowns[session_id] - time.time()
            return max(0, int(remaining))
        return 0
