from pydantic import BaseModel, EmailStr


class UserLoginSchema(BaseModel):
    """Схема для авторизации пользователя"""

    email: EmailStr
    password: str


class UserRegisterSchema(UserLoginSchema):
    """Схема для регистрации пользователя"""

    username: str = ''


class JWTPayloadSchema(BaseModel):
    user_id: int
    expires: float
