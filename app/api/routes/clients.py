from typing import List
from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_client_service, get_order_service
from app.api.dependencies import get_current_user
from app.schemas.client_schemas import ClientCreate, ClientResponse
from app.models.client_model import Client
from app.services.client_service import ClientService
from app.services.order_service import OrderService


router = APIRouter(prefix="/clients", tags=["Клиенты"])


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
   client_data: ClientCreate,
   service: ClientService = Depends(get_client_service),
):
   return await service.create_client(client_data)


@router.get("/me", response_model=ClientResponse)
async def get_me(current_user: Client = Depends(get_current_user)):
   return current_user


@router.get("/", response_model=List[ClientResponse])
async def get_clients(service: ClientService = Depends(get_client_service)):
   return await service.get_clients()


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
   client_id: int,
   service: ClientService = Depends(get_client_service),
):
   return await service.get_client(client_id)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
   client_id: int,
   service: ClientService = Depends(get_client_service),
):
   await service.delete_client(client_id)
   return None


@router.get("/{client_id}/orders/")
async def get_client_orders(
   client_id: int,
   service: OrderService = Depends(get_order_service),
):
   """Получить все заказы клиента."""
   return await service.get_orders(client_id)