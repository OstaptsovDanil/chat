from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.chats import Message, UserChat, ReadCursor


async def is_user_in_chat(session: AsyncSession, user_id: int, chat_id: int) -> bool:
    """Получить список id чатов пользователя"""
    query = select(UserChat).filter_by(user_id=user_id, chat_id=chat_id)
    result = await session.execute(query)
    return bool(result.one_or_none())


async def chat_filter_by_user(session: AsyncSession, user_id: int) -> list[int]:
    """Получить список id чатов пользователя"""
    query = select(UserChat.chat_id).filter_by(user_id=user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def messages_from_chat(
    session: AsyncSession,
    chat_id: int,
    limit: int | None,
    offset: int | None,
) -> list[Message]:
    """Получить список последних сообщений из чата"""
    query = (
        select(Message)
        .filter_by(chat_id=chat_id)
        .limit(limit)
        .offset(offset)
        .order_by(Message.dt_created)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def read_cursors_from_chat(
    session: AsyncSession,
    chat_id,
) -> Sequence[ReadCursor]:
    """Получить список всех курсоров прочитки сообщения"""
    query = select(ReadCursor).filter_by(chat_id=chat_id)
    result = await session.execute(query)
    return result.scalars().all()


async def message_filter_by_id(session: AsyncSession, message_id: int) -> Message:
    query = select(Message).filter_by(id=message_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def message_create(session: AsyncSession, user_id: int, chat_id: int, message_text: str) -> Message:
    message = Message(user_id=user_id, chat_id=chat_id, text=message_text)
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def message_read(session: AsyncSession, user_id: int, chat_id: int, message: Message):
    query = select(ReadCursor).filter_by(user_id=user_id, chat_id=chat_id).with_for_update()
    result = await session.execute(query)

    read_cursor: ReadCursor = result.scalar_one()
    new_message_id = max(message.id, read_cursor.message_id) if read_cursor.message_id else message.id
    read_cursor.message_id = new_message_id
    await session.commit()
    await session.refresh(message)
