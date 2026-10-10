from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

from app.core.database import Base
from app.models.associative_tables import flower_order_association

if TYPE_CHECKING:
   from app.models.client_model import Client
   from app.models.flower_model import Flower

   
class OrderStatus(str, Enum):
   PENDING = "pending"
   PROCESSING = "processing"
   COMPLETED = "completed"
   CANCELLED = "cancelled"


class Order(Base):
   __tablename__ = "orders"

   id: Mapped[int] = mapped_column(primary_key=True)
   client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
   order_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
   status: Mapped[str] = mapped_column(default=OrderStatus.PENDING.value)
   total_amount: Mapped[Optional[float]] = mapped_column(default=0.0)

   client: Mapped["Client"] = relationship(
      "Client",
      back_populates="orders"
   )

   flowers: Mapped[List["Flower"]] = relationship(
      "Flower",
      secondary=flower_order_association,
      back_populates="orders"
   )