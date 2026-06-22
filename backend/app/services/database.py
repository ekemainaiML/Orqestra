from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.services.settings import settings

_engine = None
_async_session = None


def _ensure_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url, echo=settings.debug)
    return _engine


def _ensure_async_session():
    global _async_session
    if _async_session is None:
        _async_session = async_sessionmaker(_ensure_engine(), class_=AsyncSession, expire_on_commit=False)
    return _async_session


def get_engine():
    return _ensure_engine()


def get_async_session():
    return _ensure_async_session()


class Base(DeclarativeBase):
    pass


async def get_session():
    async with get_async_session()() as session:
        try:
            yield session
        finally:
            await session.close()
