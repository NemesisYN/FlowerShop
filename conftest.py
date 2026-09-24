import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app, Base, get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session():
   """Создаёт чистую БД для каждого теста и удаляет после."""
   async with test_engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)

   async with TestSession() as session:
      yield session

   async with test_engine.begin() as conn:
      await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
   """Тестовый HTTP-клиент, который использует тестовую БД."""
   async def override_get_db():
      yield db_session

   app.dependency_overrides[get_db] = override_get_db

   transport = ASGITransport(app=app)
   async with AsyncClient(transport=transport, base_url="http://test") as ac:
      yield ac

   app.dependency_overrides.clear()