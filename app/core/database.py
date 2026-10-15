from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import app_config
from typing import AsyncGenerator


engine = create_async_engine(app_config.DATABASE_URL, echo=True)
AsyncSessionConn = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
   """Base class for ORM models."""

   pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
   """Async's session depend for endpoints of app"""
   async with AsyncSessionConn() as session:
      try:
         yield session
      except Exception:
         await session.rollback()
         raise

