from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client_model import Client
from app.repositories.client_repo import ClientRepository
from app.schemas.client_schemas import ClientCreate
from app.core.security import hash_password


class ClientService:
   """Бизнес-логика для работы с клиентами."""

   def __init__(self, db: AsyncSession):
      self.db = db
      self.repo = ClientRepository(db)

   # === CREATE ===
   async def create_client(self, data: ClientCreate) -> Client:
      # Проверяем уникальность email
      if data.email:
         existing = await self.repo.get_by_email(data.email)
         if existing:
               raise HTTPException(
                  status_code=status.HTTP_400_BAD_REQUEST,
                  detail="Клиент с таким email уже существует",
               )

      client = Client(
         name=data.name,
         address=data.address,
         phone=data.phone,
         email=data.email,
         hashed_password=hash_password(data.password) if data.password else None,
         is_active=True,
      )
      await self.repo.create(client)

      await self.db.commit()
      await self.db.refresh(client)

      return client

   # === READ ===
   async def get_client(self, client_id: int) -> Client:
      client = await self.repo.get_by_id(client_id)
      if not client:
         raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail="Клиент не найден",
         )
      return client

   async def get_clients(self) -> list[Client]:
      return await self.repo.get_all()

   # === DELETE ===
   async def delete_client(self, client_id: int) -> None:
      client = await self.repo.get_by_id(client_id)
      if not client:
         raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail="Клиент не найден",
         )

      await self.repo.delete(client)
      await self.db.commit()