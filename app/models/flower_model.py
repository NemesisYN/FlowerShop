from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, List
from datetime import datetime

from app.core.database import Base
from app.models.associative_tables import flower_order_association
from app.models.order_model import Order


class Flower(Base):
   __tablename__ = "flowers"

   id: Mapped[int] = mapped_column(primary_key=True, index=True)
   name: Mapped[str] = mapped_column(nullable=False)
   color: Mapped[str] = mapped_column(nullable=False)
   price: Mapped[float] = mapped_column(nullable=False, default=1.0)
   stock_quantity: Mapped[int] = mapped_column(default=0)
   description: Mapped[Optional[str]]
   created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

   orders: Mapped[List["Order"]] = relationship(
      "Order",
      secondary=flower_order_association,
      back_populates="flowers"
   )