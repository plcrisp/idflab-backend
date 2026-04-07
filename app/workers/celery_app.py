from celery import Celery
from app.core.config import settings

celery = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery.conf.task_routes = {
    "app.workers.tasks.*": {"queue": "default"}
}