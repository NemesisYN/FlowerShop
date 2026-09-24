import pytest

pytestmark = pytest.mark.asyncio


async def _create_client(client, name="NK"):
   r = await client.post(
      "/clients/", json={"name": name, "address": "X", "phone": None, "email": None}
   )
   return r.json()["id"]


async def _create_flower(client, name="Rose", price=100.0, stock=10):
   r = await client.post(
      "/flowers/",
      json={"name": name, "color": "Red", "price": price, "stock_quantity": stock},
   )
   return r.json()["id"]


async def test_create_order(client):
   client_id = await _create_client(client)
   flower_id = await _create_flower(client, price=100.0, stock=10)

   response = await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 2}]},
   )
   assert response.status_code == 201
   data = response.json()
   assert data["client_id"] == client_id
   assert data["total_amount"] == 200.0


async def test_create_order_client_not_found(client):
   flower_id = await _create_flower(client)
   response = await client.post(
      "/orders/",
      json={"client_id": 99999, "items": [{"flower_id": flower_id, "quantity": 1}]},
   )
   assert response.status_code == 404


async def test_create_order_flower_not_found(client):
   client_id = await _create_client(client)
   response = await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": 99999, "quantity": 1}]},
   )
   assert response.status_code == 404


async def test_create_order_not_enough_stock(client):
   client_id = await _create_client(client)
   flower_id = await _create_flower(client, stock=2)

   response = await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 100}]},
   )
   assert response.status_code == 400


async def test_get_orders(client):
   client_id = await _create_client(client)
   flower_id = await _create_flower(client, stock=10)

   await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 1}]},
   )

   response = await client.get("/orders/")
   assert response.status_code == 200
   assert len(response.json()) == 1


async def test_get_orders_filter_by_status(client):
   client_id = await _create_client(client)
   flower_id = await _create_flower(client, stock=10)

   await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 1}]},
   )

   response = await client.get("/orders/?status=pending")
   assert response.status_code == 200
   assert len(response.json()) == 1

   response_empty = await client.get("/orders/?status=completed")
   assert response_empty.json() == []


async def test_get_order(client):
   client_id = await _create_client(client)
   flower_id = await _create_flower(client, stock=10)

   create = await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 2}]},
   )
   order_id = create.json()["id"]

   response = await client.get(f"/orders/{order_id}")
   assert response.status_code == 200
   assert response.json()["id"] == order_id
   assert len(response.json()["items"]) == 1


async def test_get_order_not_found(client):
   response = await client.get("/orders/99999")
   assert response.status_code == 404


async def test_update_order_status(client):
   client_id = await _create_client(client)
   flower_id = await _create_flower(client, stock=10)

   create = await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 1}]},
   )
   order_id = create.json()["id"]

   response = await client.patch(f"/orders/{order_id}/status?status=processing")
   assert response.status_code == 200


async def test_update_order_status_invalid(client):
   client_id = await _create_client(client)
   flower_id = await _create_flower(client, stock=10)

   create = await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 1}]},
   )
   order_id = create.json()["id"]

   response = await client.patch(f"/orders/{order_id}/status?status=invalid_status")
   assert response.status_code == 400


async def test_update_order_status_not_found(client):
   response = await client.patch("/orders/99999/status?status=completed")
   assert response.status_code == 404


async def test_cancel_order_returns_stock(client):
   """При отмене заказа товар возвращается на склад."""
   client_id = await _create_client(client)
   flower_id = await _create_flower(client, stock=10)

   await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 3}]},
   )

   # Проверяем, что склад уменьшился
   flower = await client.get(f"/flowers/{flower_id}")
   assert flower.json()["stock_quantity"] == 7

   # Отменяем заказ
   order_id = (await client.get("/orders/")).json()[0]["id"]
   await client.patch(f"/orders/{order_id}/status?status=cancelled")

   # Проверяем, что склад вернулся
   flower = await client.get(f"/flowers/{flower_id}")
   assert flower.json()["stock_quantity"] == 10


async def test_delete_order(client):
   client_id = await _create_client(client)
   flower_id = await _create_flower(client, stock=10)

   create = await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 1}]},
   )
   order_id = create.json()["id"]

   response = await client.delete(f"/orders/{order_id}")
   assert response.status_code == 204


async def test_delete_order_not_found(client):
   response = await client.delete("/orders/99999")
   assert response.status_code == 404