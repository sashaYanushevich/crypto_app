from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime

class UserBase(BaseModel):
    tg_id: str
    username: str
    coins: int
    tokens: int
    tickets: int
    language: Optional[str] = None
    region: Optional[str] = None
    

class UserCreateBase(BaseModel):
    tg_id: str
    username: str
    language: Optional[str] = None
    region: Optional[str] = None
    parent_id: Optional[int] = None
    
class UserCreate(BaseModel):
    init_data: Dict[str, Any] 
    
    
class UserInDBBase(UserBase):
    id: int
    registration_date: datetime

    class Config:
        from_attributes = True 

class User(UserInDBBase):
    pass
