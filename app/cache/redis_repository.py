import json
from typing import Optional, Any

import redis.asyncio as redis

from app.core.config import app_config


class RedisRepository:
   def __init__(self):
      self.REDIS_URL = app_config.REDIS_URL
      self.redis_client = redis.from_url(self.REDIS_URL, decode_responses=True) 

   async def cache_get(self, key: str) -> Optional[Any]:
      client = self.redis_client
      value = await client.get(key)

      if value is None:
         return None

      return json.loads(value)


   async def cache_set(self, key: str, value: Any, ttl: int = 60) -> None:
      client = self.redis_client
      serialized = json.dumps(value, default=str)

      await client.set(key, serialized, ex=ttl)


   async def cache_delete_pattern(self, pattern: str) -> None:
      client = self.redis_client

      async for key in client.scan_iter(match=pattern):
         await client.delete(key)


redis_repo = RedisRepository()
