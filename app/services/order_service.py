from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order_model import Order
from app.models.order_model import OrderStatus
from app.repositories.order_repo import OrderRepository
from app.schemas.order_schemas import OrderCreate


class OrderService:
   """Бизнес-логика для работы с заказами."""

   def __init__(self, db: AsyncSession):
      self.db = db
      self.repo = OrderRepository(db)

   async def create_order(self, client_id: int, order_data: OrderCreate) -> Order:
      # 1. Проверяем клиента
      client = await self.repo.get_client(client_id)
      if not client:
         raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail="Клиент не найден",
         )

      # 2. Создаём заказ
      order = await self.repo.create(
         client_id=client_id,
         status=OrderStatus.PENDING.value,
      )

      # 3. Добавляем цветы
      total = 0
      for item in order_data.items:
         flower = await self.repo.get_flower(item.flower_id)
         if not flower:
               raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Цветок с ID {item.flower_id} не найден",
               )

         if flower.stock_quantity < item.quantity:
               raise HTTPException(
                  status_code=status.HTTP_400_BAD_REQUEST,
                  detail=(
                     f"Недостаточно {flower.name}. "
                     f"В наличии: {flower.stock_quantity}"
                  ),
               )

         flower.stock_quantity -= item.quantity

         await self.repo.add_flower(
               order_id=order.id,
               flower_id=flower.id,
               quantity=item.quantity,
         )

         total += flower.price * item.quantity

      order.total_amount = total
      await self.db.commit()

      # 4. Перезагружаем со связями
      return await self.repo.get_with_relations(order.id)


   async def get_orders(self, client_id: int, skip: int = 0, limit: int = 100, status_filter: str | None = None) -> list[Order]:
      return await self.repo.get_list(
         client_id=client_id, skip=skip, limit=limit, status=status_filter
      )


   async def get_order_detail(self, order_id: int, client_id: int) -> dict:
      order = await self.repo.get_with_relations(order_id, with_client=True)
      if not order:
         raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail="Заказ не найден",
         )

      if order.client_id != client_id:
         raise HTTPException(403, "Нет доступа к чужому заказу")

      # Один запрос вместо N в цикле
      quantities = await self.repo.get_quantities_map(order.id)

      items = [
         {
               "flower_id": flower.id,
               "name": flower.name,
               "color": flower.color,
               "price": flower.price,
               "quantity": quantities.get(flower.id, 1),
               "subtotal": flower.price * quantities.get(flower.id, 1),
         }
         for flower in order.flowers
      ]

      return {
         "id": order.id,
         "client_id": order.client_id,
         "order_date": order.order_date,
         "status": order.status,
         "total_amount": order.total_amount,
         "client": order.client,
         "items": items,
      }


   async def update_status(self, order_id: int, new_status: str, client_id: int) -> dict:
      valid_statuses = [s.value for s in OrderStatus]
      if new_status not in valid_statuses:
         raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail=f"Неверный статус. Допустимые: {valid_statuses}",
         )

      order = await self.repo.get_by_id(order_id)
      if not order:
         raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail="Заказ не найден",
         )

      if order.client_id != client_id:
         raise HTTPException(403, "Нет доступа к чужому заказу")
      
      # При отмене — возвращаем товары на склад
      if (
         new_status == OrderStatus.CANCELLED.value
         and order.status != OrderStatus.CANCELLED.value
      ):
         await self._restore_stock(order)

      order.status = new_status
      await self.db.commit()

      return {
         "message": f"Статус заказа #{order_id} обновлен на '{new_status}'"
      }


   async def _restore_stock(self, order: Order) -> None:
      """Вернуть товары на склад при отмене заказа."""
      associations = await self.repo.get_associations(order.id)

      for assoc in associations:
         flower = await self.repo.get_flower(assoc.flower_id)
         if flower:
               flower.stock_quantity += assoc.quantity


   async def delete_order(self, order_id: int, client_id: int) -> None:
      order = await self.repo.get_by_id(order_id)
      if not order:
         raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail="Заказ не найден",
         )

      if order.client_id != client_id:
         raise HTTPException(403, "Нет доступа к чужому заказу")
      
      await self.repo.delete(order)
      await self.db.commit()