from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str]
    password: Mapped[str]

    chats: Mapped[list['Chat']] = relationship(
        back_populates='users',
        secondary='users_chats',
    )
    messages: Mapped[list['Message']] = relationship(back_populates='user')
    read_cursors: Mapped[list['ReadCursor']] = relationship(back_populates='user')
