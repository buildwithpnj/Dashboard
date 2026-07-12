import os
from typing import List, Dict, Any
from app.data_ingestion.loaders.jsonl_loader import JSONLLoader
from app.data_ingestion.loaders.csv_loader import CSVLoader
from app.data_ingestion.loaders.markdown_loader import MarkdownLoader
from app.data_ingestion.loaders.pdf_loader import PDFLoader
from app.data_ingestion.normalizers import TextNormalizer
from app.data_ingestion.dedup import DocumentDeduplicator

class IngestionPipeline:
    """Orchestrates format routing, whitespace normalization, and content deduplication of imported files."""

    def __init__(self):
        self.loaders = {
            ".jsonl": JSONLLoader(),
            ".csv": CSVLoader(),
            ".md": MarkdownLoader(),
            ".pdf": PDFLoader()
        }

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Processes file inputs, performing normalization and deduplication steps."""
        _, ext = os.path.splitext(file_path.lower())
        loader = self.loaders.get(ext, self.loaders[".md"])

        raw_docs = loader.load(file_path)
        
        # Clean text encodings
        for doc in raw_docs:
            doc["content"] = TextNormalizer.normalize(doc.get("content", ""))

        # Strip duplicates
        return DocumentDeduplicator.deduplicate(raw_docs)
