from fastapi import HTTPException, status
import jwt

from datetime import datetime, timedelta, timezone

from app.core.config import app_config
from app.schemas.auth_schemas import TokenData


def create_access_token(data: dict, expires_delta: str = app_config.ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
   to_encode = data.copy()
   expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
   to_encode.update({"exp": expire, "type": "access"})
   return jwt.encode(to_encode, app_config.SECRET_KEY, algorithm=app_config.ALGORITHM)


def create_refresh_token(data: dict, expires_delta: str = app_config.REFRESH_TOKEN_EXPIRE_DAYS) -> str:
   to_encode = data.copy()
   expire = datetime.now(timezone.utc) + timedelta(days=expires_delta)
   to_encode.update({"exp": expire, "type": "refresh"})
   return jwt.encode(to_encode, app_config.SECRET_KEY, algorithm=app_config.ALGORITHM)


def decode_token(token: str) -> TokenData:
   try:
      payload = jwt.decode(token, app_config.SECRET_KEY, algorithms=[app_config.ALGORITHM])
      return TokenData(**payload)
   except jwt.ExpiredSignatureError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Expired")
   except jwt.InvalidTokenError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")