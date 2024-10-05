from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, User
from app.db.session import async_session
from app.repository.user import crud_user

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/users/", response_model=User)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user_by_tgID(db, tgID=user_in.tgID)
    if user:
        return user
    user = await crud_user.create_user(db, user_in=user_in)
    return user

@router.get("/users/{tgID}", response_model=User)
async def get_user(tgID: int, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user_by_tgID(db, tgID=tgID)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{tgID}", response_model=User)
async def update_user(tgID: int, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user_by_tgID(db, tgID=tgID)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = user_in.username
    user.region = user_in.region
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/users/{tgID}")
async def delete_user(tgID: int, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user_by_tgID(db, tgID=tgID)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"detail": "User deleted"}
