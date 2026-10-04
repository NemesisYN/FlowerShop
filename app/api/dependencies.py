from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.client_service import ClientService
from app.services.flower_service import FlowerService
from app.services.order_service import OrderService
from app.services.stats_service import StatsService


def get_client_service(db: AsyncSession = Depends(get_db)) -> ClientService:
   return ClientService(db)


def get_flower_service(db: AsyncSession = Depends(get_db)) -> FlowerService:
   return FlowerService(db)


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
   return OrderService(db)


def get_stats_service(db: AsyncSession = Depends(get_db)) -> StatsService:
   return StatsService(db)