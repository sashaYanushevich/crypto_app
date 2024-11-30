from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class PendingReferralReward(Base):
    __tablename__ = "pending_referral_rewards"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    referee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    coins = Column(Integer, default=0)
    tickets = Column(Integer, default=0)
    is_claimed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    claimed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    referrer = relationship(
        "User",
        foreign_keys=[referrer_id],
        back_populates="pending_rewards"
    )
    referee = relationship(
        "User",
        foreign_keys=[referee_id]
    ) 