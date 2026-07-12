from app.repositories.base import BaseDBRepository
from app.db.models import KnowledgeDocument

class KnowledgeDocumentsRepository(BaseDBRepository[KnowledgeDocument]):
    """DB-backed repository managing ingested document metadata files."""

    def __init__(self, db):
        super().__init__(db, KnowledgeDocument)
