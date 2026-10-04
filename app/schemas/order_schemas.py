from pydantic import BaseModel, ConfigDict, Field

from typing import Optional, List
from datetime import datetime

from app.schemas.flower_schemas import FlowerResponse
from app.schemas.client_schemas import ClientResponse


class OrderItem(BaseModel):
   flower_id: int
   quantity: int = Field(ge=1, description="Количество цветов")

class OrderCreate(BaseModel):
   client_id: int
   items: List[OrderItem]  # список цветов с количеством

class OrderResponse(BaseModel):
   id: int
   client_id: int
   order_date: datetime
   status: str
   total_amount: Optional[float]
   flowers: List[FlowerResponse]
   
   model_config = ConfigDict(from_attributes=True)

class OrderDetailResponse(BaseModel):
   id: int
   client_id: int
   order_date: datetime
   status: str
   total_amount: Optional[float]
   client: ClientResponse
   items: List[dict]  # будет содержать цветы с количеством