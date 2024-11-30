from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.db.session import async_session
from app.core.security import get_current_user
from app.models.game_sessions import GameSession
from app.models.user import User
from app.models.earnings import Earning
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

class GameSessionStart(BaseModel):
    game_type: str

class GameSessionEnd(BaseModel):
    session_id: int
    coins_earned: int
    score: int

class LeaderboardEntry(BaseModel):
    username: str
    score: int
    rank: int

class LeaderboardResponse(BaseModel):
    leaderboard: List[LeaderboardEntry]
    me: Optional[LeaderboardEntry] = None

@router.post("/games/start")
async def start_game_session(
    game_data: GameSessionStart,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start a new game session"""
    session = GameSession(
        user_id=current_user.id,
        game_type=game_data.game_type,
        status='active'
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return {"session_id": session.id}

@router.post("/games/end")
async def end_game_session(
    game_data: GameSessionEnd,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """End a game session and process rewards"""
    # Get the session
    session = await db.get(GameSession, game_data.session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != 'active':
        raise HTTPException(status_code=400, detail="Session already ended")

    # Update session
    session.coins_earned = game_data.coins_earned
    session.score = game_data.score
    session.end_time = datetime.utcnow()
    session.status = 'completed'

    # Get user
    user = await db.get(User, current_user.id)
    
    # Update user's coins
    user.coins += game_data.coins_earned

    # Create earnings record
    earning = Earning(
        user_id=current_user.id,
        amount=game_data.coins_earned,
        currency='coins',
        source_type='game_reward',
        source_id=session.id
    )
    db.add(earning)

    # Update high scores - handle None values safely
    now = datetime.utcnow()
    
    # All-time high score
    current_high_score = user.game_high_score or 0
    if game_data.score > current_high_score:
        user.game_high_score = game_data.score
    
    # Weekly/Daily high scores
    current_daily_score = user.daily_high_score or 0
    current_weekly_score = user.weekly_high_score or 0
    
    if not user.last_score_update or user.last_score_update.date() != now.date():
        user.daily_high_score = game_data.score
    elif game_data.score > current_daily_score:
        user.daily_high_score = game_data.score

    if not user.last_score_update or (now - user.last_score_update).days >= 7:
        user.weekly_high_score = game_data.score
    elif game_data.score > current_weekly_score:
        user.weekly_high_score = game_data.score

    user.last_score_update = now

    await db.commit()
    
    return {
        "success": True,
        "coins_earned": game_data.coins_earned,
        "new_high_score": user.game_high_score == game_data.score,
        "scores": {
            "current_score": game_data.score,
            "all_time_high": user.game_high_score,
            "weekly_high": user.weekly_high_score,
            "daily_high": user.daily_high_score
        }
    }

@router.get("/leaderboard/{period}", response_model=LeaderboardResponse)
async def get_leaderboard(
    period: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 100
):
    """Get leaderboard for specified period (all_time, weekly, daily)"""
    now = datetime.utcnow()
    
    # Base query for rank and score based on period
    if period == "all_time":
        score_column = User.game_high_score
        where_conditions = [User.game_high_score > 0]
    elif period == "weekly":
        score_column = User.weekly_high_score
        week_ago = now - timedelta(days=7)
        where_conditions = [
            User.weekly_high_score > 0,
            User.last_score_update >= week_ago
        ]
    elif period == "daily":
        score_column = User.daily_high_score
        today = now.date()
        where_conditions = [
            User.daily_high_score > 0,
            func.date(User.last_score_update) == today
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid period")

    # Query for leaderboard
    rank_query = (
        select(
            User.username,
            score_column.label('score'),
            func.rank().over(
                order_by=score_column.desc()
            ).label('rank')
        )
        .where(and_(*where_conditions))
    )

    # Get top players
    result = await db.execute(rank_query.limit(limit))
    leaderboard = result.all()

    # Get current user's rank and score
    my_rank_query = rank_query.where(User.id == current_user.id)
    my_result = await db.execute(my_rank_query)
    my_entry = my_result.first()

    # Prepare response
    response = {
        "leaderboard": [
            LeaderboardEntry(
                username=entry.username,
                score=entry.score,
                rank=entry.rank
            ) for entry in leaderboard
        ],
        "me": LeaderboardEntry(
            username=my_entry.username,
            score=my_entry.score,
            rank=my_entry.rank
        ) if my_entry else None
    }

    return response 