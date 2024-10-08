from fastapi import FastAPI, Request, Depends, HTTPException
from starlette.middleware.sessions import SessionMiddleware as StarletteSessionMiddleware
from contextlib import asynccontextmanager
from src.api.v1.endpoints import router as api_router
from src.middleware.error_handler import add_error_handlers
from src.core.config import settings
from src.redis import redis_conn
from src.core.config import app_config

# Lifespan handler for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_conn.initialize()
    yield
    await redis_conn.close()

# Initialize FastAPI with lifespan
app = FastAPI(lifespan=lifespan)

# Middleware to manage session state using Redis
@app.middleware("http")
async def redis_session_middleware(request: Request, call_next):
    redis = await redis_conn.get_redis()
    session_id = request.cookies.get("session_id")
    if session_id:
        request.state.session = await redis.get(f"session:{session_id}") or {}
    else:
        request.state.session = {}

    response = await call_next(request)

    if session_id and request.state.session:
        await redis.set(f"session:{session_id}", str(request.state.session))

    return response

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/config")
def get_config():
    return {
        "debug": app_config.DEBUG,
        "database_uri": app_config.SQLALCHEMY_DATABASE_URI,
        "secret_key": app_config.SECRET_KEY,
    }


# Add session middleware
app.add_middleware(
    StarletteSessionMiddleware, 
    secret_key=settings.session_secret_key
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Error Handling
add_error_handlers(app)

# Entry point for running the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)