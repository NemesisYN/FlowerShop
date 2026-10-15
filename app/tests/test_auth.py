import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


# === РЕГИСТРАЦИЯ ===

async def test_register_success(client: AsyncClient):
   """Успешная регистрация."""
   response = await client.post("/auth/register", json={
      "name": "Test",
      "address": "Test",
      "email": "test@test.com",
      "password": "secret123",
   })
   assert response.status_code == 201
   assert response.json()["email"] == "test@test.com"
   assert "hashed_password" not in response.json()   # пароль не должен возвращаться


async def test_register_duplicate_email(client: AsyncClient):
   """Повторная регистрация с тем же email → 400."""
   data = {
      "name": "Test", "address": "Test",
      "email": "test@test.com", "password": "secret123",
   }
   await client.post("/auth/register", json=data)
   response = await client.post("/auth/register", json=data)
   assert response.status_code == 400


# === ЛОГИН ===

async def test_login_success(client: AsyncClient):
   """Успешный логин → access + refresh токены."""
   await client.post("/auth/register", json={
      "name": "Test", "address": "Test",
      "email": "test@test.com", "password": "secret123",
   })
   response = await client.post("/auth/login", data={
      "username": "test@test.com",
      "password": "secret123",
   })
   assert response.status_code == 200
   data = response.json()
   assert "access_token" in data
   assert "refresh_token" in data
   assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
   """Неверный пароль → 401."""
   await client.post("/auth/register", json={
      "name": "Test", "address": "Test",
      "email": "test@test.com", "password": "secret123",
   })
   response = await client.post("/auth/login", data={
      "username": "test@test.com",
      "password": "wrong_password",
   })
   assert response.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
   """Несуществующий email → 401."""
   response = await client.post("/auth/login", data={
      "username": "noone@test.com",
      "password": "secret123",
   })
   assert response.status_code == 401


# === ЗАЩИЩЁННЫЕ ЭНДПОИНТЫ (ME) ===

async def test_get_me_without_token(client: AsyncClient):
   """Без токена → 401."""
   response = await client.get("/clients/me")
   assert response.status_code == 401


async def test_get_me_with_token(client: AsyncClient):
   """С токеном → 200, свой профиль."""
   await client.post("/auth/register", json={
      "name": "Test", "address": "Test",
      "email": "test@test.com", "password": "secret123",
   })
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


async def test_get_me_invalid_token(client: AsyncClient):
   """Невалидный токен → 401."""
   response = await client.get(
      "/clients/me",
      headers={"Authorization": "Bearer invalid_token"},
   )
   assert response.status_code == 401


# === LOGOUT (ЧЁРНЫЙ СПИСОК) ===

async def test_logout_and_token_blacklisted(client: AsyncClient):
   """После logout токен попадает в чёрный список."""
   await client.post("/auth/register", json={
      "name": "Test", "address": "Test",
      "email": "test@test.com", "password": "secret123",
   })
   login = await client.post("/auth/login", data={
      "username": "test@test.com", "password": "secret123",
   })
   token = login.json()["access_token"]
   headers = {"Authorization": f"Bearer {token}"}

   # 1. До logout — /me работает
   me_before = await client.get("/clients/me", headers=headers)
   assert me_before.status_code == 200

   # 2. Logout
   logout = await client.post("/auth/logout", headers=headers)
   assert logout.status_code == 204

   # 3. После logout — /me должен вернуть 401
   me_after = await client.get("/clients/me", headers=headers)
   assert me_after.status_code == 401