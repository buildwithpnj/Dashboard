from celery import Celery
from app.core.config import settings

# Initialize Celery app instance with Redis settings
celery_app = Celery(
    "warborn_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes maximum limit per task
)

# Discover tasks under app/tasks
celery_app.autodiscover_tasks(["app.tasks"])
