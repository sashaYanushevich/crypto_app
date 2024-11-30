from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Earning(Base):
    __tablename__ = "earnings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)  # 'coins', 'tokens', 'tickets'
    source_type = Column(String, nullable=False)  # 'task_completion', 'referral', etc.
    source_id = Column(Integer, nullable=True)  # Reference to task_id or other sources
    date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="earnings")
