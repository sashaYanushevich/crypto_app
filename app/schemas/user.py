# app/schemas/user.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    tgID: int
    username: str
    region: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserInDBBase(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 

class User(UserInDBBase):
    pass
