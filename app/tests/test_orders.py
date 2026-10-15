import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def _register_and_login(client: AsyncClient, email: str = "test@test.com") -> str:
   """Регистрирует клиента и возвращает access_token."""
   await client.post("/auth/register", json={
      "name": "Test", "address": "Test",
      "email": email, "password": "secret123",
   })
   login = await client.post("/auth/login", data={
      "username": email, "password": "secret123",
   })
   return login.json()["access_token"]


async def _create_flower(client: AsyncClient, name: str = "Rose", stock: int = 10) -> int:
   """Создаёт цветок и возвращает его ID."""
   response = await client.post("/flowers/", json={
      "name": name, "color": "Red", "price": 100.0, "stock_quantity": stock,
   })
   return response.json()["id"]


# 1. Создание заказа (с токеном)
async def test_create_order(client: AsyncClient):
   token = await _register_and_login(client)
   headers = {"Authorization": f"Bearer {token}"}
   flower_id = await _create_flower(client, stock=10)

   response = await client.post("/orders/", json={
      "items": [{"flower_id": flower_id, "quantity": 2}],
   }, headers=headers)

   assert response.status_code == 201
   assert response.json()["total_amount"] == 200.0


# 2. Создание без токена → 401
async def test_create_order_without_token(client: AsyncClient):
   flower_id = await _create_flower(client, stock=10)
   response = await client.post("/orders/", json={
      "items": [{"flower_id": flower_id, "quantity": 2}],
   })
   assert response.status_code == 401


# 3. Недостаточно товара на складе → 400
async def test_create_order_not_enough_stock(client: AsyncClient):
   token = await _register_and_login(client)
   headers = {"Authorization": f"Bearer {token}"}
   flower_id = await _create_flower(client, stock=1)

   response = await client.post("/orders/", json={
      "items": [{"flower_id": flower_id, "quantity": 100}],
   }, headers=headers)
   assert response.status_code == 400


# 4. GET /orders/ — только свои заказы
async def test_get_orders_only_own(client: AsyncClient):
   # Клиент 1 создаёт заказ
   token1 = await _register_and_login(client, "first@test.com")
   flower_id = await _create_flower(client, stock=10)
   await client.post("/orders/", json={
      "items": [{"flower_id": flower_id, "quantity": 1}],
   }, headers={"Authorization": f"Bearer {token1}"})

   # Клиент 2 — не должен видеть заказ клиента 1
   token2 = await _register_and_login(client, "second@test.com")
   response = await client.get(
      "/orders/",
      headers={"Authorization": f"Bearer {token2}"},
   )
   assert response.status_code == 200
   assert response.json() == []


# 5. GET /orders/{id} — чужой заказ → 403
async def test_get_foreign_order(client: AsyncClient):
   # Клиент 1 создаёт заказ
   token1 = await _register_and_login(client, "first@test.com")
   flower_id = await _create_flower(client, stock=10)
   create = await client.post("/orders/", json={
      "items": [{"flower_id": flower_id, "quantity": 1}],
   }, headers={"Authorization": f"Bearer {token1}"})
   order_id = create.json()["id"]

   # Клиент 2 — пытается посмотреть чужой заказ
   token2 = await _register_and_login(client, "second@test.com")
   response = await client.get(
      f"/orders/{order_id}",
      headers={"Authorization": f"Bearer {token2}"},
   )
   assert response.status_code == 403