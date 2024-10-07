from fastapi import APIRouter
from src.api.v1.schemas import Item
from src.auth.auth import create_access_token, verify_password, get_password_hash
from src.models.user import User
from datetime import timedelta
from jose import JWTError
from src.auth.auth import has_role
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter
from fastapi import APIRouter, HTTPException
from ...app import app
from src.core.config import settings 


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"token": token}

app.include_router(router, prefix="/api/v1")

@router.post("/items/", summary="Create an Item", description="Endpoint to create a new item.")
async def create_item(item: Item):
    return {"item": item}

fake_users_db = {
    "user1": {
        "username": "user1",
        "email": "user1@example.com",
        "password": get_password_hash("password1"),
        "is_active": True,
        "is_admin": False,
        "roles": ["user"]
    }
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    print(user)
    if not user or not verify_password(password, user["password"]):
        return False
    return user

@router.post("/login")
async def login_for_access_token(form_data: User):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/admin-dashboard")
async def admin_dashboard(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Invalid token")
    except:
        raise HTTPException(status_code=403, detail="Invalid token")

    if not has_role(payload, "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    return {"admin_data": "secret_admin_data"}