from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserInventory(Base):
    __tablename__ = "user_inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    quantity = Column(Integer, default=1)

    # Relationships
    user = relationship("User", back_populates="inventory")
    inventory_item = relationship("InventoryItem", back_populates="users")
