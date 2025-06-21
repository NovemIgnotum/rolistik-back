from beanie import Document
from pydantic import EmailStr, Field
from typing import Optional
from datetime import datetime, timezone

class User(Document):
    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_gamemaster: bool = False
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Settings:
        name = "users"
        use_state_management = True