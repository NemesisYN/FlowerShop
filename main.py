from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from sqlalchemy import ForeignKey, Table, Column, Integer, select, delete, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
import os
from dotenv import load_dotenv

from cache import cache_get, cache_set, cache_delete_pattern

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
   raise ValueError("DATABASE_URL не задан!")

# # Проверка на работоспособность ->
# load_dotenv()
# print("DATABASE_URL:", os.getenv("DATABASE_URL"))
# print("Все переменные:", {k: v for k, v in os.environ.items() if k.isupper()})

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionConn = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
   pass

# ============ ПРОМЕЖУТОЧНАЯ ТАБЛИЦА ============
flower_order_association = Table(
   "order_flowers", 
   Base.metadata,
   Column("order_id", ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True),
   Column("flower_id", ForeignKey("flowers.id", ondelete="CASCADE"), primary_key=True),
   Column("quantity", Integer, default=1)
)

# ============ МОДЕЛИ ORM ============
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

class Flower(Base):
   __tablename__ = "flowers"

   id: Mapped[int] = mapped_column(primary_key=True)
   name: Mapped[str] = mapped_column(nullable=False)
   color: Mapped[str] = mapped_column(nullable=False)
   price: Mapped[float] = mapped_column(nullable=False, default=11.0)
   stock_quantity: Mapped[int] = mapped_column(default=0)
   description: Mapped[Optional[str]]
   created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

   orders: Mapped[List["Order"]] = relationship(
      "Order",
      secondary=flower_order_association,
      back_populates="flowers"
   )

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
   total_amount: Mapped[Optional[float]] = mapped_column(default=0)

   client: Mapped["Client"] = relationship(
      "Client",
      back_populates="orders"
   )

   flowers: Mapped[List["Flower"]] = relationship(
      "Flower",
      secondary=flower_order_association,
      back_populates="orders"
   )

# ============ PYDANTIC СХЕМЫ (DTO) ============
class ClientCreate(BaseModel):
   name: str
   address: str
   phone: Optional[str] = None
   email: Optional[str] = None

class ClientResponse(BaseModel):
   id: int
   name: str
   address: str
   phone: Optional[str]
   email: Optional[str]
   
   model_config = ConfigDict(from_attributes=True)

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

class OrderItem(BaseModel):
   flower_id: int
   quantity: int = Field(ge=1, description="Количество цветов")

class OrderCreate(BaseModel):
   client_id: int
   items: List[OrderItem]  # список цветов с количеством

class OrderResponse(BaseModel):
   id: int
   client_id: int
   order_date: datetime
   status: str
   total_amount: Optional[float]
   flowers: List[FlowerResponse]
   
   model_config = ConfigDict(from_attributes=True)

class OrderDetailResponse(BaseModel):
   id: int
   client_id: int
   order_date: datetime
   status: str
   total_amount: Optional[float]
   client: ClientResponse
   items: List[dict]  # будет содержать цветы с количеством

class PopularFlowerResponse(BaseModel):
   id: int
   name: str
   order_count: int
   total_sold: int

# ============ ЗАВИСИМОСТЬ ДЛЯ БД ============
async def get_db():
   async with AsyncSessionConn() as session:
      yield session

# ============ LIFESPAN ============
@asynccontextmanager
async def lifespan(app: FastAPI):
   print("Приложение запускается...")
   yield
   print("Приложение завершает работу...")
   await engine.dispose()

# ============ FASTAPI ПРИЛОЖЕНИЕ ============
app = FastAPI(
   lifespan=lifespan, 
   title="FLOWER SHOP", 
   description="Приложение по заказу цветов в районе твоего города",
   version="1.0.0"
)

app.add_middleware(
   CORSMiddleware, 
   allow_headers=["*"],
   allow_methods=["*"],
   
)
# ============ ЭНДПОИНТЫ ДЛЯ КЛИЕНТОВ ============

@app.get("/", tags=["Главная"])
async def show_main_page():
   return {"message": "Добро пожаловать в цветочный магазин!"}

@app.post("/clients/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, tags=["Клиенты"])
async def create_client(client_data: ClientCreate, db: AsyncSession = Depends(get_db)):
   # Проверяем, нет ли клиента с таким email
   if client_data.email:
      existing = await db.execute(
         select(Client).where(Client.email == client_data.email)
      )
      if existing.scalar_one_or_none():
         raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail="Клиент c таким email уже существует"
         )
   
   # Создаём клиента
   new_client = Client(**client_data.model_dump())
   db.add(new_client)
   await db.commit()
   await db.refresh(new_client)
   return new_client

@app.get("/clients/", response_model=List[ClientResponse], tags=["Клиенты"])
async def get_clients(db: AsyncSession = Depends(get_db)):
   """Получить всех клиентов"""
   result = await db.execute(select(Client))
   return result.scalars().all()

@app.get("/clients/{client_id}", response_model=ClientResponse, tags=["Клиенты"])
async def get_client(client_id: int, db: AsyncSession = Depends(get_db)):
   """Получить клиента по ID"""
   client = await db.get(Client, client_id)
   if not client:
      raise HTTPException(status_code=404, detail="Клиент не найден")
   return client

@app.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Клиенты"])
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db)):
   """Удалить клиента"""
   client = await db.get(Client, client_id)
   if not client:
      raise HTTPException(status_code=404, detail="Клиент не найден")
   await db.delete(client)
   await db.commit()

# ============ ЭНДПОИНТЫ ДЛЯ ЦВЕТОВ ============

@app.post("/flowers/", response_model=FlowerResponse, status_code=status.HTTP_201_CREATED, tags=["Цветы"])
async def create_flower(flower_data: FlowerCreate, db: AsyncSession = Depends(get_db)):
   """Добавить новый цветок"""
   flower = Flower(**flower_data.model_dump())
   db.add(flower)
   await db.commit()
   await cache_delete_pattern("flowers:*")
   await db.refresh(flower)
   return flower

@app.get("/flowers/", response_model=List[FlowerResponse], tags=["Цветы"])
async def get_flowers(
   skip: int = 0, 
   limit: int = 100,
   db: AsyncSession = Depends(get_db)
):
   """Получить все цветы (с пагинацией)"""

   redis_key = f"flowers:skip={skip}:limit={limit}"
   cached = await cache_get(redis_key)

   if cached is not None:
      print("<FROM CACHE get all flowers>")
      return cached
   else:
      print("<FROM DATABASE get all flowers>")
      result = await db.execute(select(Flower).offset(skip).limit(limit))
      flowers = result.scalars().all()
      flowers_data = [FlowerResponse.model_validate(f).model_dump() for f in flowers]
      await cache_set(redis_key, flowers_data, ttl=300)
      return flowers_data


@app.get("/flowers/{flower_id}", response_model=FlowerResponse, tags=["Цветы"])
async def get_flower(flower_id: int, db: AsyncSession = Depends(get_db)):
   """Получить цветок по ID"""

   redis_key = f"flowers:{flower_id}"
   cached = await cache_get(redis_key)

   if cached is not None:
      print(f"<FROM CACHE get flower {cached['name']}>")
      return cached
   
   flower = await db.get(Flower, flower_id)
   if not flower:
      print("<THE DATABASE DOESN'T HAVE THIS FLOWER>")
      raise HTTPException(status_code=404, detail="Цветок не найден")

   print(f"<FROM DATABASE get flower {flower.name}>")
   flower_data = FlowerResponse.model_validate(flower).model_dump()
   await cache_set(redis_key, flower_data, ttl=300)
   return flower_data

@app.patch("/flowers/{flower_id}/stock", tags=["Цветы"])
async def update_stock(
   flower_id: int, 
   quantity: int, 
   db: AsyncSession = Depends(get_db)
):
   """Обновить количество цветов на складе"""
   flower = await db.get(Flower, flower_id)
   if not flower:
      raise HTTPException(status_code=404, detail="Цветок не найден")
   
   if flower.stock_quantity + quantity < 0:
      raise HTTPException(status_code=400, detail="Недостаточно товара на складе")
   
   flower.stock_quantity += quantity
   await db.commit()
   return {"message": f"Склад обновлен. Теперь: {flower.stock_quantity} шт."}

@app.delete("/flowers/all", status_code=status.HTTP_204_NO_CONTENT, tags=["Цветы"])
async def delete_flowers(db: AsyncSession = Depends(get_db)):
   """Удалить все цветы"""
   await db.execute(delete(Flower))
   await db.commit()
   await cache_delete_pattern("flowers:*")


@app.delete("/flowers/{flower_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Цветы"])
async def delete_flower(flower_id: int, db: AsyncSession = Depends(get_db)):
   """Удалить цветок"""
   flower = await db.get(Flower, flower_id)
   if not flower:
      raise HTTPException(status_code=404, detail="Цветок не найден")
   await db.delete(flower)
   await db.commit()
   await cache_delete_pattern("flowers:*")

# ============ ЭНДПОИНТЫ ДЛЯ ЗАКАЗОВ ============

from sqlalchemy import select
from sqlalchemy.orm import selectinload

@app.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Заказы"])
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
   """Создать новый заказ"""
   # Проверяем клиента
   client = await db.get(Client, order_data.client_id)
   if not client:
      raise HTTPException(status_code=404, detail="Клиент не найден")
   
   # Создаем заказ
   order = Order(
      client_id=order_data.client_id,
      status=OrderStatus.PENDING.value
   )
   db.add(order)
   await db.flush()  # получаем id заказа
   
   total = 0
   
   # Добавляем цветы в заказ
   for item in order_data.items:
      flower = await db.get(Flower, item.flower_id)
      if not flower:
         raise HTTPException(
               status_code=404,
               detail=f"Цветок с ID {item.flower_id} не найден"
         )
      
      if flower.stock_quantity < item.quantity:
         raise HTTPException(
               status_code=400,
               detail=f"Недостаточно {flower.name}. В наличии: {flower.stock_quantity}"
         )
      
      # Уменьшаем склад
      flower.stock_quantity -= item.quantity
      
      # Добавляем запись в ассоциативную таблицу
      await db.execute(
         flower_order_association.insert().values(
               order_id=order.id,
               flower_id=flower.id,
               quantity=item.quantity
         )
      )
      
      total += flower.price * item.quantity
   
   order.total_amount = total
   await db.commit()
   
   # ПЕРЕЗАГРУЖАЕМ заказ с подгрузкой flowers
   stmt = (
      select(Order)
      .options(selectinload(Order.flowers))  # Загружаем связь
      .where(Order.id == order.id)
   )
   result = await db.execute(stmt)
   order = result.scalar_one()
   
   return order

@app.get("/orders/", response_model=List[OrderResponse], tags=["Заказы"])
async def get_orders(
   skip: int = 0,
   limit: int = 100,
   status: Optional[str] = None,
   db: AsyncSession = Depends(get_db)
):
   """Получить все заказы (c фильтром по статусу)"""
   query = select(Order)
   if status:
      query = query.where(Order.status == status)
   query = query.offset(skip).limit(limit)
   
   result = await db.execute(query)
   orders = result.scalars().all()
   
   # Загружаем цветы для каждого заказа
   for order in orders:
      await db.refresh(order, attribute_names=["flowers"])
   
   return orders

@app.get("/orders/{order_id}", response_model=OrderDetailResponse, tags=["Заказы"])
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
   """Получить заказ по ID деталями"""
   # Загружаем заказ с клиентом и цветами
   query = select(Order).where(Order.id == order_id).options(
      selectinload(Order.client),
      selectinload(Order.flowers)
   )
   result = await db.execute(query)
   order = result.scalar_one_or_none()
   
   if not order:
      raise HTTPException(status_code=404, detail="Заказ не найден")
   
   # Получаем количество для каждого цветка
   items = []
   for flower in order.flowers:
      # Запрос к промежуточной таблице
      assoc = await db.execute(
         select(flower_order_association)
         .where(flower_order_association.c.order_id == order.id)
         .where(flower_order_association.c.flower_id == flower.id)
      )
      assoc_data = assoc.first()
      quantity = assoc_data.quantity if assoc_data else 1
      
      items.append({
         "flower_id": flower.id,
         "name": flower.name,
         "color": flower.color,
         "price": flower.price,
         "quantity": quantity,
         "subtotal": flower.price * quantity
      })
   
   return {
      "id": order.id,
      "client_id": order.client_id,
      "order_date": order.order_date,
      "status": order.status,
      "total_amount": order.total_amount,
      "client": order.client,
      "items": items
   }

@app.patch("/orders/{order_id}/status", tags=["Заказы"])
async def update_order_status(
   order_id: int,
   status: str,
   db: AsyncSession = Depends(get_db)
):
   """Обновить статус заказа"""
   valid_statuses = [s.value for s in OrderStatus]
   if status not in valid_statuses:
      raise HTTPException(
         status_code=400, 
         detail=f"Неверный статус. Допустимые: {valid_statuses}"
      )
   
   order = await db.get(Order, order_id)
   if not order:
      raise HTTPException(status_code=404, detail="Заказ не найден")
   
   # Если заказ отменяем - возвращаем товары на склад
   if status == OrderStatus.CANCELLED.value and order.status != OrderStatus.CANCELLED.value:
      # Получаем все позиции заказа
      assoc_query = await db.execute(
         select(flower_order_association)
         .where(flower_order_association.c.order_id == order.id)
      )
      associations = assoc_query.all()
      
      for assoc in associations:
         flower = await db.get(Flower, assoc.flower_id)
         if flower:
               flower.stock_quantity += assoc.quantity
   
   order.status = status
   await db.commit()
   
   return {"message": f"Статус заказа #{order_id} обновлен на '{status}'"}

@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Заказы"])
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
   """Удалить заказ"""
   order = await db.get(Order, order_id)
   if not order:
      raise HTTPException(status_code=404, detail="Заказ не найден")
   
   await db.delete(order)
   await db.commit()

# ============ ДОПОЛНИТЕЛЬНЫЕ ЭНДПОИНТЫ ============

@app.get("/clients/{client_id}/orders/", tags=["Клиенты"])
async def get_client_orders(client_id: int, db: AsyncSession = Depends(get_db)):
   """Получить все заказы клиента"""
   client = await db.get(Client, client_id)
   if not client:
      raise HTTPException(status_code=404, detail="Клиент не найден")
   
   # Загружаем заказы с цветами
   query = select(Order).where(Order.client_id == client_id).options(
      selectinload(Order.flowers)
   )
   result = await db.execute(query)
   orders = result.scalars().all()
   
   return {
      "client": client.name,
      "orders": orders
   }

@app.get(
   "/stats/popular-flowers/",
   response_model=list[PopularFlowerResponse],
   tags=["Статистика"]
)
async def get_popular_flowers(
   limit: int = 10,
   db: AsyncSession = Depends(get_db)
):
   """Получить самые популярные цветы"""
   result = await db.execute(
      select(
         Flower.id,
         Flower.name,
         func.count(flower_order_association.c.order_id).label("order_count"),
         func.sum(flower_order_association.c.quantity).label("total_sold")
      )
      .join(
         flower_order_association,
         flower_order_association.c.flower_id == Flower.id
      )
      .group_by(Flower.id, Flower.name)
      .order_by(func.count(flower_order_association.c.order_id).desc())
      .limit(limit)
   )
   
   return result.mappings().all()

@app.get("/stats/orders-summary/", tags=["Статистика"])
async def get_orders_summary(db: AsyncSession = Depends(get_db)):
   """Получить сводку по заказам"""
   total_orders = await db.execute(select(func.count()).select_from(Order))
   total_revenue = await db.execute(select(func.coalesce(func.sum(Order.total_amount), 0)).select_from(Order))
   
   status_counts = {}
   for status in OrderStatus:
      count = await db.execute(
         select(func.count()).where(Order.status == status.value)
      )
      status_counts[status.value] = count.scalar()
   
   return {
      "total_orders": total_orders.scalar(),
      "total_revenue": float(total_revenue.scalar()),
      "by_status": status_counts
   }

# ============ ЗАПУСК ============
if __name__ == "__main__":
   uvicorn.run(app, host="127.0.0.1", port=8070)

