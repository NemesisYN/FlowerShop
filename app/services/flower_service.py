from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis_repository import redis_repo
from app.models.flower_model import Flower
from app.repositories.flower_repo import FlowerRepository
from app.schemas.flower_schemas import FlowerCreate, FlowerResponse


class FlowerService:
    """Бизнес-логика для работы с цветами."""

    CACHE_TTL = 300

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FlowerRepository(db)

    # === CREATE ===
    async def create_flower(self, data: FlowerCreate) -> Flower:
        flower = Flower(**data.model_dump())
        await self.repo.create(flower)

        await self.db.commit()
        await self.db.refresh(flower)

        await redis_repo.cache_delete_pattern("flowers:*")

        return flower

    # === READ — список ===
    async def get_flowers(self, skip: int = 0, limit: int = 100):
        cache_key = f"flowers:skip={skip}:limit={limit}"

        cached = await redis_repo.cache_get(cache_key)
        if cached is not None:
            print("<FROM CACHE get all flowers>")
            return cached

        print("<FROM DATABASE get all flowers>")
        flowers = await self.repo.get_all(offset=skip, limit=limit)

        flowers_data = [
            FlowerResponse.model_validate(f).model_dump()
            for f in flowers
        ]
        await redis_repo.cache_set(cache_key, flowers_data, ttl=self.CACHE_TTL)

        return flowers_data

    # === READ — один ===
    async def get_flower(self, flower_id: int):
        cache_key = f"flowers:{flower_id}"

        cached = await redis_repo.cache_get(cache_key)
        if cached is not None:
            print(f"<FROM CACHE get flower {cached['name']}>")
            return cached

        flower = await self.repo.get_by_id(flower_id)
        if not flower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Цветок не найден",
            )

        flower_data = FlowerResponse.model_validate(flower).model_dump()
        await redis_repo.cache_set(cache_key, flower_data, ttl=self.CACHE_TTL)

        return flower_data

    # === UPDATE — склад ===
    async def update_stock(self, flower_id: int, quantity: int) -> dict:
        flower = await self.repo.get_by_id(flower_id)
        if not flower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Цветок не найден",
            )

        if flower.stock_quantity + quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недостаточно товара на складе",
            )

        flower.stock_quantity += quantity
        await self.db.commit()

        await redis_repo.cache_delete_pattern("flowers:*")

        return {
            "message": f"Склад обновлен. Теперь: {flower.stock_quantity} шт."
        }

    # === DELETE — один ===
    async def delete_flower(self, flower_id: int) -> None:
        flower = await self.repo.get_by_id(flower_id)
        if not flower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Цветок не найден",
            )

        await self.repo.delete(flower)
        await self.db.commit()

        await redis_repo.cache_delete_pattern("flowers:*")

    # === DELETE — все ===
    async def delete_all_flowers(self) -> None:
        await self.repo.delete_all()
        await self.db.commit()

        await redis_repo.cache_delete_pattern("flowers:*")