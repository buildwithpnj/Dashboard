import csv
from typing import List, Dict, Any
from app.data_ingestion.loaders.base import BaseLoader

class CSVLoader(BaseLoader):
    """Parses CSV files converting row entries into document strings."""

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        docs = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Compile text representing row properties
                content = ", ".join(f"{k}: {v}" for k, v in row.items())
                docs.append({
                    "content": content,
                    "metadata": dict(row)
                })
        return docs
