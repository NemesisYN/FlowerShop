from pydantic import BaseModel, ConfigDict

from typing import Optional


class ClientCreate(BaseModel):
   name: str
   address: str
   phone: Optional[str] = None
   email: Optional[str] = None
   password: str | None = None


class ClientResponse(BaseModel):
   id: int
   name: str
   address: str
   phone: Optional[str]
   email: Optional[str]
   
   model_config = ConfigDict(from_attributes=True)