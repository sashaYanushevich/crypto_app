from pydantic import BaseModel
from typing import Optional, List

class InventoryItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    item_type: Optional[str] = None

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemInDB(InventoryItemBase):
    id: int

    class Config:
        from_attributes = True

class UserInventoryItem(BaseModel):
    id: int
    user_id: int
    inventory_item_id: int
    quantity: int
    inventory_item: InventoryItemInDB

    class Config:
        from_attributes = True

class AddInventoryItem(BaseModel):
    item_id: int
    quantity: Optional[int] = 1

class RemoveInventoryItem(BaseModel):
    item_id: int
    quantity: Optional[int] = 1 