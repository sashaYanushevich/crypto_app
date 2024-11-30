from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    reward_coins = Column(Integer, default=0)
    reward_tokens = Column(Integer, default=0)
    reward_tickets = Column(Integer, default=0)
    link = Column(String, nullable=True)
    additional_info = Column(Text, nullable=True)
    type = Column(String, nullable=False)

    # Relationships
    users = relationship("UserTask", back_populates="task")
