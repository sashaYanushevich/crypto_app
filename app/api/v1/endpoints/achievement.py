from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/achievement/")
async def get_achievements(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"achievement": ["achievement1", "achievement2", "achievement3"], "user": current_user}
