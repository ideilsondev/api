from celery import Celery
from app.core.config import settings

celery = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)