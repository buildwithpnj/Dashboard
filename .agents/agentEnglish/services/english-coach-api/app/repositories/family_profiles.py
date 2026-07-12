from typing import Optional
from sqlalchemy import select
from app.repositories.base import BaseDBRepository
from app.db.models import FamilyProfile

class FamilyProfilesRepository(BaseDBRepository[FamilyProfile]):
    """DB-backed storage repository managing family member profiles (languages, contacts)."""

    def __init__(self, db):
        super().__init__(db, FamilyProfile)
