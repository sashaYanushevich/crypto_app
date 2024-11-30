from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(String, nullable=True)

    # Relationships
    users = relationship("UserInventory", back_populates="inventory_item")
