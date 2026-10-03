import os
from celery import Celery

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")

celery_app = Celery(
   "notifications",
   broker=CELERY_BROKER_URL,
   include=["celery_tasks"] # Celery ищет задачи в файле celery_tasks.py
)

celery_app.conf.update(
   task_serializer="json",
   accept_content=["json"],
   result_serializer="json",
   timezone="UTC",
   enable_utc=True,
)