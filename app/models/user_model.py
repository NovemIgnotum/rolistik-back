from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    username: str
    email: str
    hash_password: str = Field(..., min_length=8, max_length=128)
    campaign: Optional[str] = None
    is_admin: bool = False
    is_gm: bool = False