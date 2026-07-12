from typing import List, Dict, Any
from app.data_ingestion.loaders.base import BaseLoader

class PDFLoader(BaseLoader):
    """Parses PDF document content with dynamic pypdf extraction or fallbacks."""

    def load(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            content = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
            return [{
                "content": content,
                "metadata": {"source_path": file_path, "pages_count": len(reader.pages)}
            }]
        except ImportError:
            # Graceful local fallback if pypdf is uninstalled
            with open(file_path, "rb") as f:
                raw_bytes = f.read(200)
            return [{
                "content": f"Fallback PDF text extraction: {str(raw_bytes)}",
                "metadata": {"source_path": file_path, "pypdf_missing": True}
            }]
