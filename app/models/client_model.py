from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, List, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
   from app.models.order_model import Order


class Client(Base):
   __tablename__ = "clients"

   id: Mapped[int] = mapped_column(primary_key=True)
   name: Mapped[str] = mapped_column(nullable=False)
   address: Mapped[str] = mapped_column(nullable=False)
   phone: Mapped[Optional[str]]
   email: Mapped[Optional[str]]

   orders: Mapped[List["Order"]] = relationship(
      "Order", 
      back_populates="client", 
      cascade="all, delete-orphan"
   )