from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import async_session
from app.core.security import get_current_user
from app.repository.inventory import crud_inventory
from app.schemas.inventory import (
    InventoryItemInDB,
    UserInventoryItem,
    AddInventoryItem,
    RemoveInventoryItem
)

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/inventory/items", response_model=List[InventoryItemInDB])
async def get_available_items(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all available inventory items"""
    items = await crud_inventory.get_all_items(db)
    return items

@router.get("/inventory/my", response_model=List[UserInventoryItem])
async def get_user_inventory(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current user's inventory"""
    inventory = await crud_inventory.get_user_inventory(db, current_user.id)
    return inventory

@router.post("/inventory/add", response_model=UserInventoryItem)
async def add_to_inventory(
    item: AddInventoryItem,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add item to user's inventory"""
    inventory_item = await crud_inventory.add_item_to_inventory(
        db,
        current_user.id,
        item.item_id,
        item.quantity
    )
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return inventory_item

@router.post("/inventory/remove")
async def remove_from_inventory(
    item: RemoveInventoryItem,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove item from user's inventory"""
    success = await crud_inventory.remove_item_from_inventory(
        db,
        current_user.id,
        item.item_id,
        item.quantity
    )
    if not success:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
    return {"success": True} 