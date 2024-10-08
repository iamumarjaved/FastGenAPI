from pydantic import BaseModel

# Pydantic model for Item
class ItemModel(BaseModel):
    name: str
    owner_id: int

    class Config:
        from_attributes = True

# Pydantic model for User
class UserModel(BaseModel):
    email: str
    items: list[ItemModel] = []

    class Config:
        from_attributes = True
