from pydantic import BaseModel, ConfigDict

from typing import Optional


class FlowerCreate(BaseModel):
   name: str
   color: str
   price: float = 0.0
   stock_quantity: int = 0
   description: Optional[str] = None


class FlowerResponse(BaseModel):
   id: int
   name: str
   color: str
   price: float
   stock_quantity: int
   description: Optional[str]
   
   model_config = ConfigDict(from_attributes=True)


class PopularFlowerResponse(BaseModel):
   id: int
   name: str
   order_count: int
   total_sold: int