from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    stars_amount: int
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    invoice_id: str
    payment_url: str
    amount: float
    stars_amount: int
    expires_at: str

class PaymentDB(BaseModel):
    id: int
    invoice_id: str
    amount: float
    stars_amount: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    description: Optional[str]

    class Config:
        from_attributes = True 