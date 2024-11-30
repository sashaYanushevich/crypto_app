from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    game_type = Column(String, nullable=False)  # Type of game being played
    coins_earned = Column(Integer, default=0)
    score = Column(Integer, default=0)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default='active')  # active, completed

    # Relationships
    user = relationship("User", back_populates="game_sessions") 