from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class CharacterFile(BaseModel):
    name : str = Field(..., min_length=1, max_length=100)
    description : Optional[str] = Field(None, max_length=500)
    image_url : Optional[str] = Field(None, max_length=500)
    campaign: Optional[str] = Field(None)
    capacities: Optional[Dict[str, Dict[str, str]]] = Field(default_factory=dict)
    is_valid: bool = True
    is_from: str
