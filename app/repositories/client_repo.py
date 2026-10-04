from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client_model import Client


class ClientRepository:
   def __init__(self, db: AsyncSession):
      self.db = db

   async def get_by_id(self, client_id: int) -> Client | None:
      return await self.db.get(Client, client_id)

   async def get_by_email(self, email: str) -> Client | None:
      result = await self.db.execute(
         select(Client).where(Client.email == email)
      )
      return result.scalar_one_or_none()

   async def get_all(self) -> List[Client]:
      result = await self.db.execute(select(Client))
      return list(result.scalars().all())

   async def create(self, client: Client) -> Client:
      self.db.add(client)
      await self.db.flush()   # ← id получен, но НЕ коммитим
      return client

   async def delete(self, client: Client) -> None:
      await self.db.delete(client)
      # без commit — коммит в сервисе