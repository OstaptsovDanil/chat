import enum

from sqlalchemy import ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.database.types import intpk


class ChatType(enum.Enum):
    """Типы чатов"""

    direct = 'direct'
    group = 'group'


class Role(enum.Enum):
    """Роли в чатах"""

    owner = 'owner'
    admin = 'admin'
    member = 'member'


class Chat(Base):
    """Таблица чатов в БД"""

    __tablename__ = 'chats'

    id: Mapped[intpk]
    name: Mapped[str]
    type: Mapped[ChatType]

    messages: Mapped[list['Message']] = relationship(back_populates='chat')
    users: Mapped[list['User']] = relationship(
        back_populates='chats',
        secondary='users_chats'
    )
    read_cursors: Mapped[list['ReadCursor']] = relationship(back_populates='chat')


class Message(Base):
    """Таблица сообщений в БД"""

    __tablename__ = 'messages'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'))
    text: Mapped[str] = mapped_column(String(5000))

    user: Mapped['User'] = relationship(back_populates='messages')
    chat: Mapped['Chat'] = relationship(back_populates='messages')


class UserChat(Base):
    """Связь пользователя с чатом"""

    __tablename__ = 'users_chats'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'), primary_key=True)
    role: Mapped[Role]


class ReadCursor(Base):
    """Курсор прочитки сообщений"""

    __tablename__ = 'read_cursors'

    id: Mapped[intpk]
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    # id последнего прочитанного сообщения
    message_id: Mapped[int | None]

    chat: Mapped['Chat'] = relationship(back_populates='read_cursors')
    user: Mapped['User'] = relationship(back_populates='read_cursors')

    __table_args__ = (
        UniqueConstraint('chat_id', 'user_id', name='read_cursors_user_chat_unique'),
    )
