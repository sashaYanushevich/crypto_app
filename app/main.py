from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.api.v1.endpoints import users, achievement, tasks, referrals, payments, games, inventory
from app.core.config import settings
import logging
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.bot import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

app = FastAPI(title="Telegram WebApp Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(achievement.router, prefix=settings.API_V1_STR, tags=["achievements"])
app.include_router(tasks.router, prefix=settings.API_V1_STR, tags=["tasks"])
app.include_router(referrals.router, prefix=settings.API_V1_STR, tags=["referrals"])
app.include_router(payments.router,prefix="/api/v1",tags=["payments"])
app.include_router(games.router, prefix=settings.API_V1_STR, tags=["games"])
app.include_router(inventory.router, prefix=settings.API_V1_STR, tags=["inventory"])


# Create aiohttp app for webhook handling
aiohttp_app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)