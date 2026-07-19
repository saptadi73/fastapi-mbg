from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config.settings import Settings
from app.support.exceptions.base import ServiceUnavailableException

engine: AsyncEngine | None = None
session_factory: async_sessionmaker[AsyncSession] | None = None


async def initialize_database(settings: Settings) -> None:
    global engine, session_factory

    if not settings.database_url:
        engine = None
        session_factory = None
        return

    engine = create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_recycle=settings.database_pool_recycle,
        echo=settings.database_echo,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def close_database() -> None:
    global engine, session_factory

    if engine is not None:
        await engine.dispose()
    engine = None
    session_factory = None


async def get_db_session() -> AsyncIterator[AsyncSession]:
    if session_factory is None:
        raise ServiceUnavailableException(
            code="DATABASE_NOT_CONFIGURED",
            message="Database belum dikonfigurasi.",
        )

    async with session_factory() as session:
        yield session


async def database_is_ready() -> bool:
    if engine is None:
        return False

    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return True
