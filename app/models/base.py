from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional

class BaseModel(Document):
    created_at: datetime = Field(default_factory=datetime.now(datetime.timestamp))
    updated_at: Optional[datetime] = None 
    
    class Settings:
        use_state_management = True