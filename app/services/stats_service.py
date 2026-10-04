from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.flower_repo import FlowerRepository
from app.repositories.order_repo import OrderRepository


class StatsService:
   """Бизнес-логика для статистики."""

   def __init__(self, db: AsyncSession):
      self.db = db
      self.flower_repo = FlowerRepository(db)
      self.order_repo = OrderRepository(db)

   async def get_popular_flowers(self, limit: int = 10):
      """Самые популярные цветы."""
      return await self.flower_repo.get_popular(limit=limit)

   async def get_orders_summary(self) -> dict:
      """Сводка по заказам."""
      return await self.order_repo.get_summary()