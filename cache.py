import os
import json
from typing import Optional, Any
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0") 

redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
   global redis_client
   if redis_client is None:
      redis_client = redis.from_url(REDIS_URL, decode_responses=True)
   return redis_client


async def cache_get(key: str) -> Optional[Any]:
   client = await get_redis()
   value = await client.get(key)

   if value is None:
      return None

   return json.loads(value)


async def cache_set(key: str, value: Any, ttl: int = 60) -> None:
   client = await get_redis()
   serialized = json.dumps(value, default=str)

   await client.set(key, serialized, ex=ttl)


async def cache_delete_pattern(pattern: str) -> None:
   client = await get_redis()

   async for key in client.scan_iter(match=pattern):
      await client.delete(key)



