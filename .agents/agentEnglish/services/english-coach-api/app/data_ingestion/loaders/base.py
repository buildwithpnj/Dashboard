from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLoader(ABC):
    """Abstract interface defining document parser configurations."""

    @abstractmethod
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        """Parses target file path returning list of document dictionaries containing text content."""
        pass
