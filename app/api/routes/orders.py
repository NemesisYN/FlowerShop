from typing import Optional, List
from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_order_service
from app.schemas.order_schemas import OrderCreate, OrderResponse, OrderDetailResponse
from app.services.order_service import OrderService
from app.tasks.celery_tasks import send_order_email


router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, service: OrderService = Depends(get_order_service)):
   order = await service.create_order(order_data)

   # Celery: не роняем роут при ошибке
   try:
      send_order_email.delay(order.id, "client@example.com")
   except Exception:
      pass

   return order


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
   skip: int = 0,
   limit: int = 100,
   status_filter: Optional[str] = None,
   service: OrderService = Depends(get_order_service),
):
   return await service.get_orders(
      skip=skip, limit=limit, status_filter=status_filter
   )


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(order_id: int, service: OrderService = Depends(get_order_service)):
   return await service.get_order_detail(order_id)


@router.patch("/{order_id}/status")
async def update_order_status(
   order_id: int,
   status: str,
   service: OrderService = Depends(get_order_service),
):
   return await service.update_status(order_id, status)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, service: OrderService = Depends(get_order_service)):
   await service.delete_order(order_id)
   return None