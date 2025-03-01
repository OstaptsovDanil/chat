from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users import User
from src.users.services.auth import get_user_id_from_access_token


async def user_filter_by_email(session: AsyncSession, email: str) -> User | None:
    """Получить  пользователя по почте.

    :param session: Сессия подключения к БД.
    :param email: Электронная почта пользователя.
    :return: Пользователь из БД, если есть. Иначе - None.
    """
    query = select(User).filter_by(email=email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def user_filter_by_id(session: AsyncSession, user_id: int) -> User:
    """Получить  пользователя по почте.

    :param session: Сессия подключения к БД.
    :param user_id: Id пользователя.
    :return: Пользователь из БД, если есть.
    """
    query = select(User).filter_by(id=user_id)
    result = await session.execute(query)
    return result.scalar_one()


async def user_filter_by_token(session: AsyncSession, token: str) -> User:
    user_id = get_user_id_from_access_token(token)
    return await user_filter_by_id(session, user_id)


async def user_create_from_credentials(session: AsyncSession, username: str, email: str, hashed_password: str):
    """Создает пользователя в БД.

    :param session: Сессия подключения к БД.
    :param email: Электронная почта пользователя.
    :param username: Имя пользователя.
    :param hashed_password: Захэшоварнный пароль.
    :return: Созданный пользователь.
    """
    user = User(
        username=username,
        email=email,
        password=hashed_password,
    )
    session.add(user)
    await session.commit()

    return user
