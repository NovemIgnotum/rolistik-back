from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    
    app_name: str = "Rolistik API"
    debug: bool = False
    version: str = "1.0.0"
    
    # MongoDB settings
    mongodb_url: str
    database_name: str
    
    # Security
    secret_key: str
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # CORS
    allowed_origins: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        
settings = Settings()