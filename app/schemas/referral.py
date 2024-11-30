from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ReferralStats(BaseModel):
    referee_id: int
    referee_username: str
    total_earnings: int
    registration_date: datetime

class PendingRewards(BaseModel):
    total_coins: int
    total_tickets: int
    rewards_from: List[ReferralStats]

class ReferralList(BaseModel):
    referral_id: int
    username: str
    registration_date: datetime
    total_earned: int
    indirect_referrals_count: int

    class Config:
        from_attributes = True 