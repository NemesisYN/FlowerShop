from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.jwt import decode_token
from app.repositories.blacklist_repo import BlacklistRepository
from app.services.client_service import ClientService
from app.services.flower_service import FlowerService
from app.services.order_service import OrderService
from app.services.stats_service import StatsService
from app.services.auth_service import AuthService
from app.models.client_model import Client


def get_client_service(db: AsyncSession = Depends(get_db)) -> ClientService:
   return ClientService(db)


def get_flower_service(db: AsyncSession = Depends(get_db)) -> FlowerService:
   return FlowerService(db)


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
   return OrderService(db)


def get_stats_service(db: AsyncSession = Depends(get_db)) -> StatsService:
   return StatsService(db)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
   return AuthService(db)

def get_blacklist_repository(db: AsyncSession = Depends(get_db)):
   return BlacklistRepository(db)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
      token: str = Depends(oauth2_scheme), 
      db: AsyncSession = Depends(get_db),
      blacklist_repo: BlacklistRepository = Depends(get_blacklist_repository)
   ) -> Client:
   """Достаёт текущего пользователя из JWT."""
   
   if await blacklist_repo.is_blacklisted(token):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The Token was revoked")
   
   payload = decode_token(token).model_dump()
   user_id = payload.get("sub")
   if not user_id:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

   client = await db.get(Client, int(user_id))
   if not client:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
   if not client.is_active:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account has deactivated")

   return client
