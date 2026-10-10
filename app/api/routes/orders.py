from typing import Optional, List
from fastapi import APIRouter, Depends, status

from app.models.client_model import Client
from app.api.dependencies import get_order_service
from app.schemas.order_schemas import OrderCreate, OrderResponse, OrderDetailResponse
from app.services.order_service import OrderService
from app.tasks.celery_tasks import send_order_email
from app.api.dependencies import get_current_user


router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate,
   current_user: Client = Depends(get_current_user), 
   service: OrderService = Depends(get_order_service)
):
   order = await service.create_order(client_id=current_user.id, order_data=order_data)

   # Celery: не роняем роут при ошибке
   try:
      send_order_email.delay(order.id, current_user.email)
   except Exception:
      pass

   return order


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
   skip: int = 0,
   limit: int = 100,
   status_filter: Optional[str] = None,
   current_user: Client = Depends(get_current_user),
   service: OrderService = Depends(get_order_service),
):
   return await service.get_orders(
      client_id=current_user.id, skip=skip, limit=limit, status_filter=status_filter
   )


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(order_id: int,
   current_user: Client = Depends(get_current_user), 
   service: OrderService = Depends(get_order_service)
):
   return await service.get_order_detail(order_id=order_id, client_id=current_user.id)


@router.patch("/{order_id}/status")
async def update_order_status(
   order_id: int,
   status: str,
   current_user: Client = Depends(get_current_user),
   service: OrderService = Depends(get_order_service),
):
   return await service.update_status(order_id, status, client_id=current_user.id)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int,
   current_user: Client = Depends(get_current_user),
   service: OrderService = Depends(get_order_service)
):
   await service.delete_order(order_id, client_id=current_user.id)
   return None