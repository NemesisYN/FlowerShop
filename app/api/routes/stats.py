from typing import List
from fastapi import APIRouter, Depends

from app.api.dependencies import get_stats_service
from app.schemas.flower_schemas import PopularFlowerResponse
from app.services.stats_service import StatsService


router = APIRouter(prefix="/stats", tags=["Статистика"])


@router.get("/popular-flowers/", response_model=List[PopularFlowerResponse])
async def get_popular_flowers(limit: int = 10, service: StatsService = Depends(get_stats_service),):
   return await service.get_popular_flowers(limit=limit)


@router.get("/orders-summary/")
async def get_orders_summary(service: StatsService = Depends(get_stats_service)):
   return await service.get_orders_summary()