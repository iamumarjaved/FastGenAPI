from fastapi import FastAPI
from src.core.config import settings

# Initialize FastAPI app with Swagger and ReDoc URLs
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url
)