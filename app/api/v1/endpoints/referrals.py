from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import async_session
from app.core.security import TokenData, get_current_user
from app.models.user import User
from app.models.pending_referral_rewards import PendingReferralReward
from app.models.earnings import Earning
from app.schemas.referral import PendingRewards, ReferralList
from datetime import datetime

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/referrals/pending-rewards", response_model=PendingRewards)
async def get_pending_rewards(
    db: AsyncSession = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user)
):
    """Get all unclaimed rewards from referrals"""
    # Get full user object
    user_result = await db.execute(
        select(User).where(User.id == current_user_token.id)
    )
    current_user = user_result.scalar_one_or_none()
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get pending rewards
    query = select(PendingReferralReward).where(
        PendingReferralReward.referrer_id == current_user.id,
        PendingReferralReward.is_claimed == False
    )
    result = await db.execute(query)
    pending_rewards = result.scalars().all()

    # Calculate totals
    total_coins = sum(reward.coins for reward in pending_rewards)
    total_tickets = sum(reward.tickets for reward in pending_rewards)

    # Get referee details
    rewards_from = []
    for reward in pending_rewards:
        referee_result = await db.execute(
            select(User).where(User.id == reward.referee_id)
        )
        referee = referee_result.scalar_one()
        if referee:
            rewards_from.append({
                "referee_id": referee.id,
                "referee_username": referee.username,
                "total_earnings": reward.coins,
                "registration_date": referee.registration_date
            })

    return PendingRewards(
        total_coins=total_coins,
        total_tickets=total_tickets,
        rewards_from=rewards_from
    )

@router.post("/referrals/claim-rewards")
async def claim_rewards(
    db: AsyncSession = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user)
):
    """Claim all pending rewards"""
    # Get full user object
    user_result = await db.execute(
        select(User).where(User.id == current_user_token.id)
    )
    current_user = user_result.scalar_one_or_none()
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all unclaimed rewards
    query = select(PendingReferralReward).where(
        PendingReferralReward.referrer_id == current_user.id,
        PendingReferralReward.is_claimed == False
    )
    result = await db.execute(query)
    pending_rewards = result.scalars().all()

    if not pending_rewards:
        raise HTTPException(status_code=404, detail="No pending rewards found")

    total_coins = 0
    total_tickets = 0

    # Process all rewards
    for reward in pending_rewards:
        total_coins += reward.coins
        total_tickets += reward.tickets
        
        # Mark as claimed
        reward.is_claimed = True
        reward.claimed_at = datetime.utcnow()

        # Create earnings record
        if reward.coins > 0:
            earning = Earning(
                user_id=current_user.id,
                amount=reward.coins,
                currency='coins',
                source_type='referral_reward',
                source_id=reward.referee_id,
                notes=f'Referral reward from user {reward.referee_id}'
            )
            db.add(earning)

    # Update user's balance
    current_user.coins += total_coins
    current_user.tickets += total_tickets

    await db.commit()
    await db.refresh(current_user)
    
    return {
        "claimed_coins": total_coins,
        "claimed_tickets": total_tickets,
        "new_balance": {
            "coins": current_user.coins,
            "tickets": current_user.tickets
        },
        "success": True
    }

@router.get("/referrals/list", response_model=List[ReferralList])
async def get_referrals_list(
    db: AsyncSession = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user)
):
    """Get list of all referrals and their statistics"""
    # Get full user object
    user_result = await db.execute(
        select(User).where(User.id == current_user_token.id)
    )
    current_user = user_result.scalar_one_or_none()
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get direct referrals
    query = select(User).where(User.parent_id == current_user.id)
    result = await db.execute(query)
    referrals = result.scalars().all()

    referral_list = []
    for referral in referrals:
        # Get total earnings from this referral
        earnings_query = select(func.sum(Earning.amount)).where(
            Earning.user_id == current_user.id,
            Earning.source_id == referral.id,
            Earning.source_type.in_(['referral_reward', 'referral_earnings'])
        )
        earnings_result = await db.execute(earnings_query)
        total_earned = earnings_result.scalar() or 0

        # Count indirect referrals
        indirect_query = select(func.count(User.id)).where(User.parent_id == referral.id)
        indirect_result = await db.execute(indirect_query)
        indirect_count = indirect_result.scalar() or 0

        referral_list.append(ReferralList(
            referral_id=referral.id,
            username=referral.username,
            registration_date=referral.registration_date,
            total_earned=total_earned,
            indirect_referrals_count=indirect_count
        ))

    return referral_list 