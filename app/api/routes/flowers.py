from typing import List
from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_flower_service
from app.schemas.flower_schemas import FlowerCreate, FlowerResponse
from app.services.flower_service import FlowerService


router = APIRouter(prefix="/flowers", tags=["Цветы"])


@router.post("/", response_model=FlowerResponse, status_code=status.HTTP_201_CREATED)
async def create_flower(flower_data: FlowerCreate, service: FlowerService = Depends(get_flower_service)):
   return await service.create_flower(flower_data)


@router.get("/", response_model=List[FlowerResponse])
async def get_flowers(
   skip: int = 0,
   limit: int = 100,
   service: FlowerService = Depends(get_flower_service),
):
   return await service.get_flowers(skip=skip, limit=limit)


@router.get("/{flower_id}", response_model=FlowerResponse)
async def get_flower(flower_id: int, service: FlowerService = Depends(get_flower_service)):
   return await service.get_flower(flower_id)


@router.patch("/{flower_id}/stock")
async def update_stock(
   flower_id: int, 
   quantity: int, 
   service: FlowerService = Depends(get_flower_service)
):
   return await service.update_stock(flower_id, quantity)


@router.delete("/all", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_flowers(service: FlowerService = Depends(get_flower_service)):
   await service.delete_all_flowers()
   return None


@router.delete("/{flower_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flower(flower_id: int, service: FlowerService = Depends(get_flower_service)):
   await service.delete_flower(flower_id)
   return None