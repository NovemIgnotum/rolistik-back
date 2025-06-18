from typing import Optional
from app.core.security import get_password_hash, verify_password
from app.models.users import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user import UserRepository

class UserService:
    def __init__(self):
        self.repository = UserRepository()
    
    async def create_user(self, user_in: UserCreate) -> User:
        user_data = user_in.model_dump()
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        return await self.repository.create_user(user_data)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.repository.get_by_email(email)