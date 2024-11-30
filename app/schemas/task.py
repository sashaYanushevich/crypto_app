from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    reward_coins: int = 0
    reward_tokens: int = 0
    reward_tickets: int = 0
    link: Optional[str] = None
    additional_info: Optional[str] = None
    type: str

class TaskInDB(TaskBase):
    id: int

    class Config:
        orm_mode = True

class UserTaskBase(BaseModel):
    user_id: int
    task_id: int
    status: Optional[str] = "pending"
    last_completed_date: Optional[datetime] = None

class UserTaskUpdate(BaseModel):
    status: str
    last_completed_date: Optional[datetime] = None

class UserTaskInDB(UserTaskBase):
    id: int
    task_id: int
    status: str
    
    class Config:
        from_attributes = True

class UserTaskComplete(BaseModel):
    id: int
    status: str
    user_id: int
    task_id: int
    last_completed_date: Optional[datetime]

    class Config:
        from_attributes = True
