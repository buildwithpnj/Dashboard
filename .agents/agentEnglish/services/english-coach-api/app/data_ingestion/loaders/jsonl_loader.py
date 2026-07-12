import json
from typing import List, Dict, Any
from app.data_ingestion.loaders.base import BaseLoader

class JSONLLoader(BaseLoader):
    """Parses JSONL files extracting raw text content and metadata mappings."""

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        docs = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                # Map standard content and fallback fields
                content = data.get("text") or data.get("content") or json.dumps(data)
                docs.append({
                    "content": content,
                    "metadata": data.get("metadata") or data
                })
        return docs
