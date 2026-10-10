from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client_model import Client
from app.models.flower_model import Flower
from app.models.order_model import Order
from app.models.associative_tables import flower_order_association

from app.models.order_model import OrderStatus


class OrderRepository:
   def __init__(self, db: AsyncSession):
      self.db = db


   # === Вспомогательные ===
   async def get_client(self, client_id: int) -> Client | None:
      return await self.db.get(Client, client_id)


   async def get_flower(self, flower_id: int) -> Flower | None:
      return await self.db.get(Flower, flower_id)


   # === Заказы ===
   async def create(self, client_id: int, status: str) -> Order:
      order = Order(client_id=client_id, status=status)
      self.db.add(order)
      await self.db.flush()
      return order


   async def get_by_id(self, order_id: int) -> Order | None:
      return await self.db.get(Order, order_id)


   async def get_with_relations(
      self, order_id: int, with_client: bool = False
   ) -> Order | None:
      options = [selectinload(Order.flowers)]
      if with_client:
         options.append(selectinload(Order.client))

      stmt = (
         select(Order)
         .options(*options)
         .where(Order.id == order_id)
      )
      result = await self.db.execute(stmt)
      return result.scalar_one_or_none()


   async def get_list(self, client_id: int, skip: int = 0, limit: int = 100, status: str | None = None) -> List[Order]:
      options = [selectinload(Order.flowers), selectinload(Order.client)]
      stmt = (
         select(Order)
         .where(Order.client_id == client_id)
         .options(*options)
         )
      if status:
         stmt = stmt.where(Order.status == status)
      stmt = stmt.offset(skip).limit(limit)

      result = await self.db.execute(stmt)
      return list(result.scalars().all())


   async def get_by_client(self, client_id: int) -> List[Order]:
      stmt = (
         select(Order)
         .where(Order.client_id == client_id)
         .options(selectinload(Order.flowers))
      )
      result = await self.db.execute(stmt)
      return list(result.scalars().all())


   async def delete(self, order: Order) -> None:
      await self.db.delete(order)


   # === Ассоциативная таблица ===
   async def add_flower(
      self, order_id: int, flower_id: int, quantity: int) -> None:
      await self.db.execute(
         flower_order_association.insert().values(
               order_id=order_id,
               flower_id=flower_id,
               quantity=quantity,
         )
      )


   async def get_associations(self, order_id: int):
      stmt = select(flower_order_association).where(
         flower_order_association.c.order_id == order_id
      )
      result = await self.db.execute(stmt)
      return result.all()


   async def get_quantities_map(self, order_id: int) -> dict[int, int]:
      """Один запрос → {flower_id: quantity}."""
      stmt = select(
         flower_order_association.c.flower_id,
         flower_order_association.c.quantity,
      ).where(flower_order_association.c.order_id == order_id)

      result = await self.db.execute(stmt)
      return {row.flower_id: row.quantity for row in result.all()}


   # === STATS ===
   async def get_summary(self) -> dict:
      total_orders = await self.db.execute(
         select(func.count()).select_from(Order)
      )
      total_revenue = await self.db.execute(
         select(func.coalesce(func.sum(Order.total_amount), 0))
      )

      status_counts = {}
      for status_enum in OrderStatus:
         count = await self.db.execute(
            select(func.count()).where(Order.status == status_enum.value)
         )
         status_counts[status_enum.value] = count.scalar()

      return {
         "total_orders": total_orders.scalar(),
         "total_revenue": float(total_revenue.scalar()),
         "by_status": status_counts,
      }