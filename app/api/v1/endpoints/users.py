from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, User, UserCreateBase
from app.db.session import async_session
from app.repository.user import crud_user
from app.core.security import create_access_token, get_current_user
from app.core.security import security
from app.repository.referral import crud_referral
from typing import Optional

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/users/init/")
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = user_in.init_data['user']
    tg_id = str(user['id'])
    username = user['username']
    referrer_id = user.get('start_param')
    user_create_base = UserCreateBase(tg_id=tg_id, username=username, language=user['language_code'], region='RU')
    existing_user = await crud_user.get_user_by_tgID(db, tg_id=tg_id)
    if existing_user:
        access_token = create_access_token(data={"sub": existing_user.id})
        return {"user": existing_user, "accessToken": access_token}
    referrer = None
    # Create new user with referrer if provided
    if referrer_id:
        referrer = await crud_user.get_user_by_tgID(db, tg_id=referrer_id)
        user_create_base.parent_id = referrer.id
    new_user = await crud_user.create_user(db, user_in=user_create_base)
    
    # Process referral rewards if there's a referrer
    if referrer:
        await crud_referral.process_referral_rewards(
            db, 
            referrer.id, 
            new_user.id,
            earned_coins=1000,  
            is_new_referral=True
        )
    
    access_token = create_access_token(data={"sub": new_user.id})
    return {"user": new_user, "accessToken": access_token}

@router.get("/users/{tgID}", response_model=User)
async def get_user(tgID: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = await crud_user.get_user_by_tgID(db, tgID=tgID)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{tgID}", response_model=User)
async def update_user(tgID: int, user_in: UserCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = await crud_user.get_user_by_tgID(db, tgID=tgID)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = user_in.username
    user.region = user_in.region
    await db.commit()
    await db.refresh(user)
    return user
