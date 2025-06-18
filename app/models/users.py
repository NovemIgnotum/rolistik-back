from beanie import Indexed
from pydantic import EmailStr, Field
from typing import Optional
from app.models.base import BaseModel

class User(BaseModel):
    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_gamemaster: bool = False
    is_superuser: bool = False
    
    class Settings:
        name = "Users"
        
class UserInDB(User):
    id: str = Field(alias="_id")
    
    class Settings:
        name = "UsersInDB"