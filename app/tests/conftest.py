import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session():
   """Создаёт чистую тестовую БД для каждого теста."""
   async with test_engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)
   async with TestSession() as session:
      yield session
   async with test_engine.begin() as conn:
      await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session):
   """HTTP-клиент с override get_db на тестовую БД."""
   async def override_get_db():
      yield db_session
   app.dependency_overrides[get_db] = override_get_db
   async with AsyncClient(
      transport=ASGITransport(app=app),
      base_url="http://test"
   ) as ac:
      yield ac
   app.dependency_overrides.clear()



@pytest.fixture(autouse=True)
def mock_redis():
   """Мокает Redis для всех тестов."""
   with patch("app.cache.redis_repository.RedisRepository.cache_delete_pattern", new_callable=AsyncMock), \
      patch("app.cache.redis_repository.RedisRepository.cache_get", new_callable=AsyncMock, return_value=None), \
      patch("app.cache.redis_repository.RedisRepository.cache_set", new_callable=AsyncMock):
      yield


@pytest.fixture(autouse=True)
def mock_celery():
   """Мокает Celery задачи."""
   with patch("app.tasks.celery_tasks.send_order_email.delay", MagicMock()):
      yield