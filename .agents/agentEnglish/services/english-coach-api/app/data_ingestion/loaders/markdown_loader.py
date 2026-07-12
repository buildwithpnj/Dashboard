from typing import List, Dict, Any
from app.data_ingestion.loaders.base import BaseLoader

class MarkdownLoader(BaseLoader):
    """Parses Markdown documentation files, preserving basic page content."""

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return [{
            "content": content,
            "metadata": {"source_path": file_path}
        }]
