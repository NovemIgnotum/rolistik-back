from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email : EmailStr
    username: str
    full_name: Optional[str] = None
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    
class UserUpdate(UserBase):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_gamemaster: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True    