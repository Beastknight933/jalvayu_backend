from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "climate_digital_twin_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Additional Celery configurations like rate limits, routing, etc., can be added here
)

# Example to discover tasks automatically
# celery_app.autodiscover_tasks(["app.workers.tasks"])
