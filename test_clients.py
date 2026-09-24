import pytest

pytestmark = pytest.mark.asyncio


async def test_create_client(client):
   response = await client.post(
      "/clients/",
      json={"name": "NK", "address": "firstnaya street", "phone": None, "email": None},
   )
   assert response.status_code == 201
   assert response.json()["name"] == "NK"
   assert response.json()["address"] == "firstnaya street"


async def test_create_client_duplicate_email(client):
   """Проверка, что клиент с таким email не создастся дважды."""
   data = {"name": "A", "address": "B", "phone": None, "email": "a@test.com"}
   first = await client.post("/clients/", json=data)
   assert first.status_code == 201

   second = await client.post("/clients/", json=data)
   assert second.status_code == 400


async def test_get_clients_empty(client):
   response = await client.get("/clients/")
   assert response.status_code == 200
   assert response.json() == []


async def test_get_clients(client):
   await client.post("/clients/", json={"name": "A", "address": "X", "phone": None, "email": None})
   await client.post("/clients/", json={"name": "B", "address": "Y", "phone": None, "email": None})

   response = await client.get("/clients/")
   assert response.status_code == 200
   assert len(response.json()) == 2


async def test_get_client(client):
   create = await client.post(
      "/clients/", json={"name": "NK", "address": "Z", "phone": None, "email": None}
   )
   client_id = create.json()["id"]

   response = await client.get(f"/clients/{client_id}")
   assert response.status_code == 200
   assert response.json()["name"] == "NK"


async def test_get_client_not_found(client):
   response = await client.get("/clients/99999")
   assert response.status_code == 404


async def test_delete_client(client):
   create = await client.post(
      "/clients/", json={"name": "NK", "address": "Z", "phone": None, "email": None}
   )
   client_id = create.json()["id"]

   response = await client.delete(f"/clients/{client_id}")
   assert response.status_code == 204

   # Проверяем, что его больше нет
   check = await client.get(f"/clients/{client_id}")
   assert check.status_code == 404


async def test_delete_client_not_found(client):
   response = await client.delete("/clients/99999")
   assert response.status_code == 404 