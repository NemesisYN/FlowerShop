import pytest

pytestmark = pytest.mark.asyncio


async def _setup_order(client):
   client_resp = await client.post(
      "/clients/", json={"name": "NK", "address": "X", "phone": None, "email": None}
   )
   client_id = client_resp.json()["id"]

   flower_resp = await client.post(
      "/flowers/",
      json={"name": "Rose", "color": "Red", "price": 100.0, "stock_quantity": 10},
   )
   flower_id = flower_resp.json()["id"]

   await client.post(
      "/orders/",
      json={"client_id": client_id, "items": [{"flower_id": flower_id, "quantity": 2}]},
   )

   return client_id, flower_id


async def test_popular_flowers(client):
   await _setup_order(client)

   response = await client.get("/stats/popular-flowers/")
   assert response.status_code == 200
   data = response.json()
   assert len(data) == 1
   assert data[0]["name"] == "Rose"
   assert data[0]["total_sold"] == 2


async def test_orders_summary(client):
   await _setup_order(client)

   response = await client.get("/stats/orders-summary/")
   assert response.status_code == 200
   data = response.json()
   assert data["total_orders"] == 1
   assert data["total_revenue"] == 200.0
   assert data["by_status"]["pending"] == 1


async def test_client_orders(client):
   client_id, _ = await _setup_order(client)

   response = await client.get(f"/clients/{client_id}/orders/")
   assert response.status_code == 200
   assert response.json()["client"] == "NK"
   assert len(response.json()["orders"]) == 1


async def test_client_orders_not_found(client):
   response = await client.get("/clients/99999/orders/")
   assert response.status_code == 404