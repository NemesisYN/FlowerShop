from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.client_repo import ClientRepository
from app.repositories.blacklist_repo import BlacklistRepository
from app.schemas.auth_schemas import RegisterRequest, Token
from app.models.client_model import Client
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token


class AuthService:
   def __init__(self, db: AsyncSession):
      self.db = db
      self.client_repo = ClientRepository(db)
      self.blacklist_repo = BlacklistRepository(db)
   
   async def register(self, data: RegisterRequest) -> Client:
      """Регистрация нового клиента."""
      existing = await self.client_repo.get_by_email(data.email)
      if existing:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user already exists in the database")

      client = Client(
         name=data.name,
         address=data.address,
         phone=data.phone,
         email=data.email,
         hashed_password=hash_password(data.password),
      )

      await self.client_repo.create(client)
      await self.db.commit()
      await self.db.refresh(client)

      return client


   async def login(self, form_data: OAuth2PasswordRequestForm) -> Token:
      """Логин: проверка пароля + выдача токенов."""
      client = await self.client_repo.get_by_email(form_data.email)
      if not client or not verify_password(form_data.password, client.hashed_password):
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Uncorrected email or password")

      if not client.is_active():
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account has deactivated")

      payload = {"sub": str(client.id), "email": client.email}
      access = create_access_token(payload)
      refresh = create_refresh_token(payload)

      return {
         "access_token": access,
         "refresh_token": refresh,
         "token_type": "bearer",
      }

   async def logout(self, token: str) -> None:
      """Добавить токен в чёрный список."""
      await self.blacklist_repo.add(token)
      await self.db.commit()