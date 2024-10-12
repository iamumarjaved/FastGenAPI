from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import aioredis
from src.core.config.config import settings

async def init_rate_limiter():
    redis = await aioredis.create_redis_pool(f"redis://{settings.redis_host}:{settings.redis_port}")
    await FastAPILimiter.init(redis)

def get_app():
    app = FastAPI()

    # Initialize rate limiter with Redis connection
    app.add_event_handler("startup", init_rate_limiter)

    return app
