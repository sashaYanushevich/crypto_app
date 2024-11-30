from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    criteria = Column(Text, nullable=True)

    # Relationships
    users = relationship("UserAchievement", back_populates="achievement")
