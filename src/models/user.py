from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str
    email: str
    is_active: bool = True
    is_admin: bool = False
    roles: list = [] 
