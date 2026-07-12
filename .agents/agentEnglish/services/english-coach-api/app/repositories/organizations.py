from app.repositories.base import BaseDBRepository
from app.db.models import Organization

class OrganizationsRepository(BaseDBRepository[Organization]):
    """DB-backed repository managing SaaS workspace organizations."""

    def __init__(self, db):
        super().__init__(db, Organization)
