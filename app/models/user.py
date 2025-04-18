from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    
class UserCreate(UserBase):
    password: str
    
class User(UserBase):
    id: int
    hashed_password: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    } 