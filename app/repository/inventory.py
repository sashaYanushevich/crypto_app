from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List, Optional
from app.models.inventory_items import InventoryItem
from app.models.user_inventory import UserInventory

class CRUDInventory:
    async def get_user_inventory(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[UserInventory]:
        """Get all items in user's inventory"""
        result = await db.execute(
            select(UserInventory)
            .where(UserInventory.user_id == user_id)
            .join(InventoryItem)
        )
        return result.scalars().all()

    async def get_all_items(
        self, 
        db: AsyncSession
    ) -> List[InventoryItem]:
        """Get all available inventory items"""
        result = await db.execute(select(InventoryItem))
        return result.scalars().all()

    async def add_item_to_inventory(
        self,
        db: AsyncSession,
        user_id: int,
        item_id: int,
        quantity: int = 1
    ) -> Optional[UserInventory]:
        """Add item to user's inventory"""
        # Check if user already has this item
        result = await db.execute(
            select(UserInventory).where(
                UserInventory.user_id == user_id,
                UserInventory.inventory_item_id == item_id
            )
        )
        user_inventory = result.scalar_one_or_none()

        if user_inventory:
            # Update quantity if item exists
            user_inventory.quantity += quantity
        else:
            # Create new inventory entry
            user_inventory = UserInventory(
                user_id=user_id,
                inventory_item_id=item_id,
                quantity=quantity
            )
            db.add(user_inventory)

        await db.commit()
        await db.refresh(user_inventory)
        return user_inventory

    async def remove_item_from_inventory(
        self,
        db: AsyncSession,
        user_id: int,
        item_id: int,
        quantity: int = 1
    ) -> bool:
        """Remove item from user's inventory"""
        result = await db.execute(
            select(UserInventory).where(
                UserInventory.user_id == user_id,
                UserInventory.inventory_item_id == item_id
            )
        )
        user_inventory = result.scalar_one_or_none()

        if not user_inventory:
            return False

        if user_inventory.quantity <= quantity:
            # Remove entire entry if quantity is less than or equal to removal amount
            await db.execute(
                delete(UserInventory).where(
                    UserInventory.user_id == user_id,
                    UserInventory.inventory_item_id == item_id
                )
            )
        else:
            # Decrease quantity
            user_inventory.quantity -= quantity

        await db.commit()
        return True

crud_inventory = CRUDInventory() 