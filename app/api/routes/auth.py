from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.client_schemas import ClientResponse
from app.schemas.auth_schemas import RegisterRequest, Token
from app.services.auth_service import AuthService
from app.api.dependencies import get_auth_service

security = HTTPBearer()


router = APIRouter(prefix='/auth', tags=['Аутентификация'])


@router.post('/register', response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, service: AuthService = Depends(get_auth_service)):
   return await service.register(data)


@router.post('/login', response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends(get_auth_service)):
   return await service.login(form_data)


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), service: AuthService = Depends(get_auth_service)):
   """Выход: добавить текущий токен в чёрный список."""
   await service.logout(credentials.credentials)

