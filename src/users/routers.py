from fastapi import APIRouter, HTTPException, status

from src.database.base import SessionDep
from src.users.schemas import UserLoginSchema, UserRegisterSchema
from src.users.services.selectors import user_filter_by_email, user_create_from_credentials
from src.users.services.auth import verify_password, hash_password, create_access_token

user_router = APIRouter(tags=['User'], prefix='/users')


@user_router.post('/login', summary='Авторизация пользователя')
async def login(credentials: UserLoginSchema, session: SessionDep):
    user = await user_filter_by_email(session, credentials.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not verify_password(credentials.password, user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(str(user.id))
    return {'access_token': access_token}


@user_router.post('/register', summary='Регистрация пользователя', status_code=status.HTTP_201_CREATED)
async def register(credentials: UserRegisterSchema, session: SessionDep):
    hashed_password = hash_password(credentials.password)
    await user_create_from_credentials(
        session,
        credentials.username,
        credentials.email,
        hashed_password,
    )
    return
