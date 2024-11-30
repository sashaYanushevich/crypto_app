from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.core.config import settings

app = FastAPI()

# Определяем схему безопасности Bearer
security = HTTPBearer()

class TokenData(BaseModel):
    id: Optional[int] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    to_encode["sub"] = str(to_encode["sub"])  
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        id: int = payload.get("sub")
        if id is None:
            raise credentials_exception
        print(f"Проверка токена: ID пользователя - {id}")  # Добавьте логирование для отладки
        return TokenData(id=id)
    except JWTError as e:
        print(f"Ошибка верификации токена: {e}")  # Лог ошибки
        raise credentials_exception


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_access_token(token, credentials_exception)


