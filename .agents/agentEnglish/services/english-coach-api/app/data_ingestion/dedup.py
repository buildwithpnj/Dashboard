import hashlib
from typing import List, Dict, Any

class DocumentDeduplicator:
    """Deduplicates ingestion lists based on SHA-256 signatures of text content."""

    @staticmethod
    def deduplicate(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique_docs = []
        for doc in documents:
            text = doc.get("content", "")
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if h not in seen:
                seen.add(h)
                unique_docs.append(doc)
        return unique_docs
