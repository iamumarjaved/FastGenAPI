from fastapi import HTTPException
import aioredis
import logging
from src.core.config import settings

# Redis Dependency Class
class RedisConnection:
    def __init__(self):
        self.redis_pool = None

    async def initialize(self):
        print("Initializing Redis connection")
        self.redis_pool = await aioredis.create_redis_pool(f"redis://{settings.redis_host}:{settings.redis_port}", encoding="utf-8")
        logging.info("Redis connection initialized")

    async def close(self):
        self.redis_pool.close()
        await self.redis_pool.wait_closed()
        logging.info("Redis connection closed")

    async def get_redis(self):
        print("Getting Redis connection")
        if self.redis_pool is None:
            raise HTTPException(status_code=503, detail="Redis connection not initialized")
        return self.redis_pool

# Global instance of RedisConnection
redis_conn = RedisConnection()