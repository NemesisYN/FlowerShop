from celery import Celery

from app.core.config import app_config 

celery_app = Celery(
   "notifications",
   broker=app_config.CELERY_BROKER_URL,
   include=["app.tasks.celery_tasks"] # Celery ищет задачи в файле celery_tasks.py
)

celery_app.conf.update(
   task_serializer="json",
   accept_content=["json"],
   result_serializer="json",
   timezone="UTC",
   enable_utc=True,
)