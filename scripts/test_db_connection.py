import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config.settings import get_settings


async def main() -> None:
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL belum diatur di file .env")

    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT current_database(), current_user, version()"))
            database_name, current_user, version = result.one()
            print("Koneksi PostgreSQL berhasil.")
            print(f"database={database_name}")
            print(f"user={current_user}")
            print(f"version={version}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
