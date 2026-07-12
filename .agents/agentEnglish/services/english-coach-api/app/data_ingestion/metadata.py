import datetime
from typing import Dict, Any, Optional, List

class MetadataBuilder:
    """Builds structured metadata dictionary fields for ingested chunks audit logs."""

    @staticmethod
    def build(
        tenant_id: str,
        product_id: str,
        source_type: str,
        source_id: str,
        language: str = "en",
        tags: Optional[List[str]] = None,
        sensitivity: str = "normal",
        quality_score: float = 1.0,
        approval_status: str = "approved"
    ) -> Dict[str, Any]:
        """Compiles clean metadata mapping dictionary for document logs."""
        return {
            "tenant_id": tenant_id,
            "product_id": product_id,
            "source_type": source_type,
            "source_id": source_id,
            "language": language,
            "tags": tags or [],
            "sensitivity": sensitivity,
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "quality_score": quality_score,
            "approval_status": approval_status
        }
