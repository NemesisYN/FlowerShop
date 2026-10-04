import os
from dotenv import load_dotenv

load_dotenv()

class AppConfigs:
   def __init__(self):
      self.DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:S3crtKfiJ4@localhost:5432/postgres")
      self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
      self.CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")

app_config = AppConfigs()