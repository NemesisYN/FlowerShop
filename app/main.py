from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.api.routes import clients, flowers, orders, stats
from app.core.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
   print("Приложение запускается...")
   yield
   print("Приложение завершает работу...")
   await engine.dispose()

app = FastAPI(
   lifespan=lifespan, 
   title="FLOWER SHOP", 
   description="Приложение по заказу цветов в районе твоего города",
   version="1.0.0"
)


app.add_middleware(
   CORSMiddleware, 
   allow_origins=["*"],
   allow_headers=["*"],
   allow_methods=["*"],
   allow_credentials=True
)

app.include_router(clients.router)
app.include_router(flowers.router)
app.include_router(orders.router)
app.include_router(stats.router)


@app.get("/", tags=["Главная"])
async def show_main_page():
   return {"message": "Добро пожаловать в цветочный магазин!"}


if __name__ == "__main__":
   uvicorn.run(app, host="127.0.0.1", port=8070)