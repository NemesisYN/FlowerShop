from sqlalchemy import Table, Column, ForeignKey, Integer

from app.core.database import Base


flower_order_association = Table(
   "order_flowers", 
   Base.metadata,
   Column("order_id", ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True),
   Column("flower_id", ForeignKey("flowers.id", ondelete="CASCADE"), primary_key=True),
   Column("quantity", Integer, default=1)
)