import pytest

pytestmark = pytest.mark.asyncio


async def test_create_flower(client):
   response = await client.post(
      "/flowers/",
      json={"name": "Rose", "color": "Red", "price": 100.0, "stock_quantity": 10},
   )
   assert response.status_code == 201
   assert response.json()["name"] == "Rose"
   assert response.json()["stock_quantity"] == 10


async def test_get_flowers_empty(client):
   response = await client.get("/flowers/")
   assert response.status_code == 200
   assert response.json() == []


async def test_get_flowers_with_pagination(client):
   for i in range(5):
      await client.post(
         "/flowers/",
         json={"name": f"Flower{i}", "color": "Red", "price": 10.0, "stock_quantity": 1},
      )

   response = await client.get("/flowers/?skip=2&limit=2")
   assert response.status_code == 200
   assert len(response.json()) == 2


async def test_get_flower(client):
   create = await client.post(
      "/flowers/",
      json={"name": "Tulip", "color": "Yellow", "price": 50.0, "stock_quantity": 5},
   )
   flower_id = create.json()["id"]

   response = await client.get(f"/flowers/{flower_id}")
   assert response.status_code == 200
   assert response.json()["name"] == "Tulip"


async def test_get_flower_not_found(client):
   response = await client.get("/flowers/99999")
   assert response.status_code == 404


async def test_update_stock_plus(client):
   create = await client.post(
      "/flowers/",
      json={"name": "Rose", "color": "Red", "price": 100.0, "stock_quantity": 5},
   )
   flower_id = create.json()["id"]

   response = await client.patch(f"/flowers/{flower_id}/stock?quantity=10")
   assert response.status_code == 200


async def test_update_stock_minus_too_much(client):
   """Попытка списать больше, чем есть — должна вернуть 400."""
   create = await client.post(
      "/flowers/",
      json={"name": "Rose", "color": "Red", "price": 100.0, "stock_quantity": 5},
   )
   flower_id = create.json()["id"]

   response = await client.patch(f"/flowers/{flower_id}/stock?quantity=-100")
   assert response.status_code == 400


async def test_update_stock_not_found(client):
   response = await client.patch("/flowers/99999/stock?quantity=5")
   assert response.status_code == 404


async def test_delete_flower(client):
   create = await client.post(
      "/flowers/",
      json={"name": "Rose", "color": "Red", "price": 100.0, "stock_quantity": 5},
   )
   flower_id = create.json()["id"]

   response = await client.delete(f"/flowers/{flower_id}")
   assert response.status_code == 204

   check = await client.get(f"/flowers/{flower_id}")
   assert check.status_code == 404

async def test_delete_flower_not_found(client):
   response = await client.delete("/flowers/99999")
   assert response.status_code == 404


async def test_delete_all_flowers(client):
   await client.post(
      "/flowers/", json={"name": "A", "color": "R", "price": 1.0, "stock_quantity": 1}
   )
   await client.post(
      "/flowers/", json={"name": "B", "color": "R", "price": 1.0, "stock_quantity": 1}
   )

   response = await client.delete("/flowers/all")
   assert response.status_code == 204

   check = await client.get("/flowers/")
   assert check.json() == []