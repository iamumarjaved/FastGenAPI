from fastapi import Request, HTTPException
from src.core.config import settings
import jwt

def role_required(role: str):
    def role_checker(request: Request):
        token = request.headers.get("Authorization").split(" ")[1]
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_roles = payload.get("roles", [])
        if role not in user_roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        return True
    return role_checker
