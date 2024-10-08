import aioredis
from fastapi import FastAPI, Request
from src.models.models import init_db, SessionLocal
from src.core.config import settings

app = FastAPI(on_startup=[init_db])

redis_pool: aioredis.Redis = None

# Dependency to get the session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
@app.on_event("startup")
async def startup_event():
    global redis_pool
    redis_pool = await aioredis.create_redis_pool(f"redis://{settings.redis_host}:{settings.redis_port}", encoding="utf-8")

@app.on_event("shutdown")
async def shutdown_event():
    redis_pool.close()
    await redis_pool.wait_closed()

@app.middleware("http")
async def redis_session_middleware(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    session = await redis_pool.get(f"session:{session_id}") if session_id else None
    request.state.session = session or {}
    response = await call_next(request)
    if request.state.session:
        await redis_pool.set(f"session:{session_id}", request.state.session)
    return response

