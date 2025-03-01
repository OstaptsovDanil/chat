from datetime import timezone, datetime, timedelta

import bcrypt
import jwt

from src.config import settings
from src.users import User
from src.users.schemas import JWTPayloadSchema


def hash_password(password: str) -> str:
    """Хэширует пароль.

    :param password: Пароль.
    :return: Захэшированный пароль.
    """
    encoded_password = password.encode()
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(encoded_password, salt).decode()


def verify_password(password: str, user: User) -> bool:
    """Проверяет, верный ли пароль.

    :param password: Пароль.
    :param user: Пользователь, для проверки пароля.
    """
    return bcrypt.checkpw(password.encode(), user.password.encode())


def create_access_token(user_id: str) -> str:
    expires = (datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
    payload = JWTPayloadSchema(user_id=user_id, expires=expires).model_dump()
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def get_user_id_from_access_token(token: str) -> int:
    payload_dict = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    data = JWTPayloadSchema(**payload_dict)

    if data.expires < datetime.now().timestamp():
        raise ValueError

    return data.user_id
