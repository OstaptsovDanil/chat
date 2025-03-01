from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

from src.config import settings

engine = create_async_engine(url=settings.database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


class Base(AsyncAttrs, DeclarativeBase):
    dt_created: Mapped[datetime] = mapped_column(server_default=func.now())
    dt_updated: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
