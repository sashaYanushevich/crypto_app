from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate

class CRUDUser:

    async def get_user_by_tgID(self, db: AsyncSession, tgID: int):
        result = await db.execute(select(User).where(User.tgID == tgID))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, user_in: UserCreate):
        user = User(**user_in.dict())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

crud_user = CRUDUser()
