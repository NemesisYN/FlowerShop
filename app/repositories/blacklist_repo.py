from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.blacklist_model import BlackList


class BlacklistRepository:
   def __init__(self, db: AsyncSession):
      self.db = db

   async def add(self, token: str) -> BlackList:
      """Добавить токен в чёрный список."""
      entry = BlackList(token=token)
      self.db.add(entry)
      await self.db.flush()
      return entry

   async def is_blacklisted(self, token: str) -> bool:
      """Проверить, есть ли токен в чёрном списке."""
      result = await self.db.execute(
         select(BlackList).where(BlackList.token == token)
      )
      return result.scalar_one_or_none()
