from fastapi import FastAPI
from app.api.v1.endpoints import users
from app.core.config import settings
import logging
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="Telegram WebApp Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")