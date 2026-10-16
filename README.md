# 🌸 FlowerShop API

Backend-приложение для цветочного магазина: управление клиентами, цветами и заказами.

## 📋 Описание

REST API на FastAPI с JWT-аутентификацией, кешированием, фоновыми задачами и миграциями.
Проект построен на слоистой архитектуре (API → Service → Repository).

## 🛠 Стек технологий

- **Язык:** Python 3.11
- **Фреймворк:** FastAPI
- **БД:** PostgreSQL + SQLAlchemy (async)
- **Миграции:** Alembic
- **Кеш:** Redis
- **Очереди:** Celery + RabbitMQ
- **Аутентификация:** JWT (PyJWT + pwdlib/Argon2)
- **Валидация:** Pydantic v2
- **Тесты:** pytest + pytest-asyncio + httpx
- **Инфраструктура:** Docker + docker-compose

## ✨ Функционал

### Клиенты
- Регистрация и логин (JWT)
- Просмотр своего профиля
- Logout с чёрным списком токенов

### Цветы
- CRUD-операции
- Пагинация
- Обновление склада

### Заказы
- Создание заказа (с проверкой склада)
- Просмотр своих заказов
- Изменение статуса (с возвратом товара при отмене)
- Фоновая отправка email через Celery

### Кеширование
- Список цветов кешируется в Redis
- Инвалидация кеша при изменении данных

## 🏗 Архитектура

```
app/
├── api/                  # Роутеры и зависимости
│   ├── routes/           # Эндпоинты
│   │   ├── auth.py
│   │   ├── clients.py
│   │   ├── flowers.py
│   │   ├── orders.py
│   │   └── stats.py
│   └── dependencies.py   # Depends (get_db, get_current_user, get_*_service)
│
├── cache/                # Работа с Redis
│   └── redis_repository.py
│
├── core/                 # Ядро приложения
│   ├── config.py         # Настройки (.env)
│   ├── database.py       # Engine, Base, get_db
│   ├── jwt.py            # Создание/проверка JWT
│   └── security.py       # Хеширование паролей (pwdlib)
│
├── models/               # SQLAlchemy-модели
│   ├── client_model.py
│   ├── flower_model.py
│   ├── order_model.py
│   ├── blacklist_model.py
│   └── associative_tables.py
│
├── repositories/         # Работа с БД (SQL)
│   ├── client_repo.py
│   ├── flower_repo.py
│   ├── order_repo.py
│   └── blacklist_repo.py
│
├── schemas/              # Pydantic-схемы
│   ├── auth_schemas.py
│   ├── client_schemas.py
│   ├── flower_schemas.py
│   └── order_schemas.py
│
├── services/             # Бизнес-логика
│   ├── auth_service.py
│   ├── client_service.py
│   ├── flower_service.py
│   ├── order_service.py
│   └── stats_service.py
│
├── tasks/                # Celery-задачи
│   ├── celery_main.py
│   └── celery_tasks.py
│
└── main.py               # Точка входа FastAPI
```

**Поток данных:** `API → Service → Repository → БД`

**Слои:**
- **API** — принимает запрос, возвращает ответ.
- **Service** — бизнес-логика (правила, проверки).
- **Repository** — работа с БД (SQL, commit).
- **Model** — структура таблиц.
- **Schema** — валидация данных (Pydantic).

## 🚀 Запуск

### Требования
- Docker + Docker Compose
- Python 3.11+

### Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/NemesisYN/flowershop.git
cd flowershop

Создать .env:
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/flowershop
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/1
SECRET_KEY=твой_секретный_ключ_минимум_32_символа
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

Запустить через Docker:
docker compose up --build -d

Открыть документацию:
http://localhost:8070/docs

🧪 Тесты
# Установить зависимости
pip install -r requirements.txt

# Запустить тесты
pytest -v

## 📡 Основные эндпоинты

### 🔐 Аутентификация

| Метод |     Путь        |  Описание              |
|-------|-----------------|------------------------|
| POST  | `/auth/register`|  Регистрация           |
| POST  | `/auth/login`   |  Логин (JWT)           |
| POST  | `/auth/logout`  |  Выход (чёрный список) |

### 👤 Клиенты

| Метод |   Путь        | Описание     |
|-------|---------------|--------------|
| GET   | `/clients/me` | Свой профиль |

### 🌸 Цветы

| Метод  | Путь                  | Описание           |
|--------|-----------------------|--------------------|
| GET    | `/flowers/`           | Список (пагинация) |
| POST   | `/flowers/`           | Создать            |
| GET    | `/flowers/{id}`       | Один цветок        |
| PATCH  | `/flowers/{id}/stock` | Обновить склад     |
| DELETE | `/flowers/{id}`       | Удалить            |

### 📦 Заказы

| Метод  |  Путь                 | Описание        |
|--------|-----------------------|-----------------|
| POST   | `/orders/`            | Создать заказ   |
| GET    | `/orders/`            | Свои заказы     |
| GET    | `/orders/{id}`        | Детали заказа   |
| PATCH  | `/orders/{id}/status` | Изменить статус |
| DELETE | `/orders/{id}`        | Удалить         |

### 📊 Статистика

| Метод |  Путь                     | Описание          |
|-------|---------------------------|-------------------|
| GET   | `/stats/popular-flowers/` | Популярные цветы  |
| GET   | `/stats/orders-summary/`  | Сводка по заказам |


👤 Автор
Никита Карелин

GitHub: @NemesisYN

Email: nikitakarel10@gmail.com