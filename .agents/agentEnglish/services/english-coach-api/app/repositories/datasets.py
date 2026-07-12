from app.repositories.base import BaseDBRepository
from app.db.models import Dataset

class DatasetsRepository(BaseDBRepository[Dataset]):
    """DB-backed repository managing datasets version configurations."""

    def __init__(self, db):
        super().__init__(db, Dataset)
