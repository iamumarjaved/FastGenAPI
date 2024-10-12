from fastapi import FastAPI, Request, Depends
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from src.api.v1.endpoints import router as api_router
from src.middleware.error_handler import add_error_handlers
from src.core.config.config import settings
from src.redis import redis_conn
from src.core.config.config import app_config
from src.security.limiter import limiter
from starlette.middleware.sessions import SessionMiddleware as StarletteSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from src.app import app


# Attach limiter state and add exception handler for rate limit errors
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"message": "Rate limit exceeded"},
))

# Add SlowAPI middleware for rate limiting
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:8000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Middleware for Redis session management
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

# Startup event to initialize Redis
@app.on_event("startup")
async def startup():
    await redis_conn.initialize()

# Apply rate limiting to a specific route
@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request):
    return {"message": "API is running"}


# Configuration route
@app.get("/config")
def get_config():
    return {
        "debug": app_config.DEBUG,
        "database_uri": app_config.SQLALCHEMY_DATABASE_URI,
        "secret_key": app_config.SECRET_KEY,
    }
    
    
@app.get("/error")
async def generate_error():
    division_by_zero = 1 / 0
    return {"result": division_by_zero}

app.include_router(api_router, prefix="/api/v1")

app.add_middleware(
    StarletteSessionMiddleware,
    secret_key=settings.session_secret_key
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
