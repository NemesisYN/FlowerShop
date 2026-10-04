from typing import List
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flower_model import Flower
from app.models.associative_tables import flower_order_association


class FlowerRepository:
   def __init__(self, db: AsyncSession):
      self.db = db

   async def get_by_id(self, flower_id: int) -> Flower | None:
      return await self.db.get(Flower, flower_id)

   async def get_all(self, offset: int = 0, limit: int = 100) -> List[Flower]:
      result = await self.db.execute(
         select(Flower).offset(offset).limit(limit)
      )
      return list(result.scalars().all())

   async def create(self, flower: Flower) -> Flower:
      self.db.add(flower)
      await self.db.flush()
      return flower

   async def delete(self, flower: Flower) -> None:
      await self.db.delete(flower)

   async def delete_all(self) -> None:
      await self.db.execute(delete(Flower))

   # === STATS ===
   async def get_popular(self, limit: int = 10):
      stmt = (
         select(
               Flower.id,
               Flower.name,
               func.count(flower_order_association.c.order_id).label("order_count"),
               func.sum(flower_order_association.c.quantity).label("total_sold"),
         )
         .join(
               flower_order_association,
               flower_order_association.c.flower_id == Flower.id,
         )
         .group_by(Flower.id, Flower.name)
         .order_by(func.count(flower_order_association.c.order_id).desc())
         .limit(limit)
      )
      result = await self.db.execute(stmt)
      return result.mappings().all()