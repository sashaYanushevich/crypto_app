from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    coins = Column(Integer, default=0)
    tokens = Column(Integer, default=0)
    tickets = Column(Integer, default=0)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    last_login_date = Column(DateTime(timezone=True), onupdate=func.now())
    region = Column(String, nullable=True)
    language = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    other_tg_data = Column(JSON, nullable=True)
    game_high_score = Column(Integer, default=0, nullable=False)
    weekly_high_score = Column(Integer, default=0, nullable=False)
    daily_high_score = Column(Integer, default=0, nullable=False)
    last_score_update = Column(DateTime(timezone=True), nullable=True)

    referrals = relationship("User", backref="parent", remote_side=[id])
    achievements = relationship("UserAchievement", back_populates="user")
    inventory = relationship("UserInventory", back_populates="user")
    tasks = relationship("UserTask", back_populates="user")
    earnings = relationship("Earning", back_populates="user")
    pending_rewards = relationship(
        "PendingReferralReward",
        foreign_keys="PendingReferralReward.referrer_id",
        back_populates="referrer"
    )
    payments = relationship("Payment", back_populates="user")
    game_sessions = relationship("GameSession", back_populates="user")
