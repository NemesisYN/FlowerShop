import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


# 1. Создание цветка (с токеном)
async def test_create_flower(client: AsyncClient):
   response = await client.post("/flowers/", json={
      "name": "Rose", "color": "Red", "price": 100.0, "stock_quantity": 10,
   })
   assert response.status_code == 201
   assert response.json()["name"] == "Rose"


# 2. Список цветов (пагинация)
async def test_get_flowers(client: AsyncClient):
   for i in range(5):
      await client.post("/flowers/", json={
         "name": f"Flower{i}", "color": "Red", "price": 10.0, "stock_quantity": 1,
      })
   response = await client.get("/flowers/?skip=0&limit=2")
   assert response.status_code == 200
   assert len(response.json()) == 2

# 3. Один цветок по ID
async def test_get_flower(client: AsyncClient):
   create = await client.post("/flowers/", json={
      "name": "Rose", "color": "Yellow", "price": 18.0, "stock_quantity": 3,
   })
   flower_id = create.json()["id"]
   response = await client.get(f"/flowers/{flower_id}")
   assert response.status_code == 200
   assert response.json()["name"] == "Rose"

# 4. Обновление склада (недостаточно товара → 400)
async def test_update_stock_too_much(client: AsyncClient):
   create = await client.post("/flowers/", json={
      "name": "Rose", "color": "Red", "price": 100.0, "stock_quantity": 5,
   })
   flower_id = create.json()["id"]
   response = await client.patch(f"/flowers/{flower_id}/stock?quantity=-100")
   assert response.status_code == 400


# 5. Удаление цветка → 204, потом 404
async def test_delete_flower(client: AsyncClient):
   create = await client.post("/flowers/", json={
      "name": "Rose", "color": "Red", "price": 100.0, "stock_quantity": 5,
   })
   flower_id = create.json()["id"]
   response = await client.delete(f"/flowers/{flower_id}")
   assert response.status_code == 204
   check = await client.get(f"/flowers/{flower_id}")
   assert check.status_code == 404