from src.api.v1.endpoints import router as api_router
from src.middleware.error_handler import add_error_handlers
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from src.app import app    

@app.get("/")
async def root():
    return {"message": "API is running"}

app.include_router(api_router, prefix="/api/v1")
# Error Handling
add_error_handlers(app)

# Entry point for running the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
