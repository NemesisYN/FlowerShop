import os
from dotenv import load_dotenv

load_dotenv()

class AppConfigs:
   def __init__(self):
      self.DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:S3crtKfiJ4@localhost:5432/postgres")
      self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
      self.CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
      self.SECRET_KEY = os.getenv("SECRET_KEY", "gISkwn7n93npPpjdmps1bT0sw17yudrfqb9")
      self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
      self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
      self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

app_config = AppConfigs()