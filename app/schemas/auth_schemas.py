from pydantic import BaseModel, EmailStr
from datetime import datetime


class Token(BaseModel):
   """Ответ при логине: два токена."""
   access_token: str
   refresh_token: str
   token_type: str = "bearer"


class TokenData(BaseModel):
   """Что кладём в JWT (payload)."""
   sub: str                 # user_id (в виде строки)
   email: str | None = None 
   exp: datetime
   type: str                # "access" или "refresh"


class LoginRequest(BaseModel):
   """Тело запроса для логина (JSON)."""
   email: EmailStr
   password: str


class RegisterRequest(BaseModel):
   """Тело запроса для регистрации."""
   name: str
   address: str
   email: EmailStr
   password: str
   phone: str | None = None