from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.models.earnings import Earning
from app.models.pending_referral_rewards import PendingReferralReward
from datetime import datetime

class CRUDReferral:
    async def process_referral_rewards(
        self, 
        db: AsyncSession, 
        referrer_id: int, 
        referee_id: int,
        earned_coins: int = 0,
        is_new_referral: bool = False
    ):
        """Process and create pending rewards for referrals"""
        
        # For new referral - create initial ticket reward
        if is_new_referral:
            pending_reward = PendingReferralReward(
                referrer_id=referrer_id,
                referee_id=referee_id,
                tickets=1,  # Initial ticket reward
                coins=0,
                is_claimed=False
            )
            db.add(pending_reward)
        
        # For earnings - calculate percentage rewards
        if earned_coins > 0:
            # Calculate 10% for direct referrer
            referrer_coins = int(earned_coins * 0.10)
            if referrer_coins > 0:
                pending_reward = PendingReferralReward(
                    referrer_id=referrer_id,
                    referee_id=referee_id,
                    coins=referrer_coins,
                    tickets=0,
                    is_claimed=False
                )
                db.add(pending_reward)
            
            # Get referrer's parent (for 2.5% indirect reward)
            referrer = await db.get(User, referrer_id)
            if referrer and referrer.parent_id:
                indirect_coins = int(earned_coins * 0.025)
                if indirect_coins > 0:
                    indirect_pending = PendingReferralReward(
                        referrer_id=referrer.parent_id,
                        referee_id=referee_id,
                        coins=indirect_coins,
                        tickets=0,
                        is_claimed=False
                    )
                    db.add(indirect_pending)
        
        await db.commit()

crud_referral = CRUDReferral() 