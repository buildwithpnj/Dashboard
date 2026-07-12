from app.repositories.base import BaseDBRepository
from app.db.models import RetrievalLog

class RetrievalLogsRepository(BaseDBRepository[RetrievalLog]):
    """DB-backed repository managing search logs and precision scores metrics."""

    def __init__(self, db):
        super().__init__(db, RetrievalLog)
