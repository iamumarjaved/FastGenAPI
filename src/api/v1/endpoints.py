from fastapi import APIRouter
from src.auth.auth import create_access_token, verify_password, get_password_hash
from src.models.models import User, Item
from src.models.pydanticModels import ItemModel, UserModel
from datetime import timedelta
from src.auth.auth import has_role
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter
from fastapi import APIRouter, HTTPException
from ...app import app
from src.core.config import settings 
from fastapi import Request
from src.auth.oauth2 import oauth
from src.middleware.role import role_required
from src.redis import redis_conn
import json
import uuid
from sqlalchemy.orm import Session
from src.api.v1.utils import get_db, to_pydantic
from src.forms.login import LoginForm



router = APIRouter()
app.include_router(router, prefix="/api/v1")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")



@app.post("/items/", response_model=ItemModel)
async def create_item(item: ItemModel, db: Session = Depends(get_db)):
    db_item = Item(name=item.name, owner_id=item.owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/users/", response_model=UserModel)
def create_user(email: str, db: Session = Depends(get_db)):
    new_user = User(email=email, hashed_password="hashed_pw")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=UserModel)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

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
    if not user or not verify_password(password, user["password"]):
        return False
    return user

@router.post("/login")
async def login_for_access_token(form_data: LoginForm): 
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


@router.get("/login/google")
async def login_via_google(request: Request):
    redis = await redis_conn.get_redis()

    # Programmatically generate a unique state and session ID
    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())  # Generate a nonce for validating the ID token
    session_id = str(uuid.uuid4())

    # Store the state and nonce in Redis with session_id as the key
    await redis.set(f"session:{session_id}", json.dumps({'state': state, 'nonce': nonce}))

    # Set the session_id as a cookie in the response
    redirect_uri = request.url_for("auth_via_google")
    response = await oauth.google.authorize_redirect(request, redirect_uri, state=state, nonce=nonce)
    response.set_cookie(key="session_id", value=session_id)  # Set session_id in cookies
    return response


@router.get("/auth/google")
async def auth_via_google(request: Request):
    redis = await redis_conn.get_redis()

    # Retrieve session_id from the cookies
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is missing")

    # Retrieve the stored session from Redis
    session_data = await redis.get(f"session:{session_id}")
    if not session_data:
        raise HTTPException(status_code=400, detail="Session expired or state missing")
    
    session = json.loads(session_data)
    stored_state = session.get('state')
    stored_nonce = session.get('nonce')  # Get the stored nonce
    received_state = request.query_params.get("state")
    
    # Check if states match
    if stored_state != received_state:
        raise HTTPException(status_code=400, detail="Mismatching state")
    
    # Complete OAuth2 flow and get the token
    token = await oauth.google.authorize_access_token(request)
    
    # Validate the ID token and nonce
    id_token = token.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="ID token is missing")
    
    # Validate the ID token using the stored nonce
    try:
        # Ensure you pass the entire token, not just id_token
        user_info = await oauth.google.parse_id_token(token, nonce=stored_nonce)
        
        # Save the user info in the token dictionary for convenience
        token['userinfo'] = user_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token validation error: {str(e)}")


    return {"token": token, "user": token.get("userinfo")}


@router.get("/admin-dashboard", dependencies=[Depends(role_required("admin"))])
async def admin_dashboard():
    return {"message": "Admin-only content"}


@router.get("/login/github")
async def login_via_github(request: Request):
    redirect_uri = request.url_for("auth_via_github")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/auth/github")
async def auth_via_github(request: Request):
    token = await oauth.github.authorize_access_token(request)
    user_info = await oauth.github.get(settings.github_userinfo_url, token=token)
    return {"user": user_info.json()}


@router.get("/login/facebook")
async def login_via_facebook(request: Request):
    redirect_uri = request.url_for("auth_via_facebook")
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@router.get("/auth/facebook")
async def auth_via_facebook(request: Request):
    token = await oauth.facebook.authorize_access_token(request)
    user_info = await oauth.facebook.get(settings.facebook_userinfo_url, token=token)
    return {"user": user_info.json()}
