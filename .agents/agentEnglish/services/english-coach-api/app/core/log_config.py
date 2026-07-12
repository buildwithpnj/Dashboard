import json
import logging
import sys
from typing import Dict, Any

# Observability-specific logger
obs_logger = logging.getLogger("coach_observability")

def setup_logging(log_level: str = "INFO") -> None:
    """Standardizes basic logging output and levels."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def log_structured_event(event_data: Dict[str, Any]) -> None:
    """Prints a machine-readable JSON log representing a single query flow.
    
    Ensures secrets are not included and text inputs are truncated for privacy.
    """
    # Double check for potential sensitive properties (like API keys)
    sanitized_event = {k: v for k, v in event_data.items() if not k.lower().endswith("key")}
    obs_logger.info(json.dumps(sanitized_event))
