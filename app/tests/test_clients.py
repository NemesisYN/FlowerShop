import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def _register(client: AsyncClient, email: str = "test@test.com"):
   """Создаёт клиента."""
   return await client.post("/auth/register", json={
      "name": "Test", "address": "Test",
      "email": email, "password": "secret123",
   })


# 1. GET /clients/ — список клиентов
async def test_get_clients(client: AsyncClient):
   await _register(client)
   response = await client.get("/clients/")
   assert response.status_code == 200
   assert len(response.json()) >= 1


# 2. GET /clients/{id} — один клиент
async def test_get_client(client: AsyncClient):
   create = await _register(client)
   client_id = create.json()["id"]
   response = await client.get(f"/clients/{client_id}")
   assert response.status_code == 200
   assert response.json()["id"] == client_id


# 3. GET /clients/{id} — не найден → 404
async def test_get_client_not_found(client: AsyncClient):
   response = await client.get("/clients/99999")
   assert response.status_code == 404


# 4. GET /clients/me — без токена → 401
async def test_get_me_without_token(client: AsyncClient):
   response = await client.get("/clients/me")
   assert response.status_code == 401


# 5. GET /clients/me — с токеном → свой профиль
async def test_get_me_with_token(client: AsyncClient):
   await _register(client)
   login = await client.post("/auth/login", data={
      "username": "test@test.com", "password": "secret123",
   })
   token = login.json()["access_token"]
   response = await client.get(
      "/clients/me",
      headers={"Authorization": f"Bearer {token}"},
   )
   assert response.status_code == 200
   assert response.json()["email"] == "test@test.com"