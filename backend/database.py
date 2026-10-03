import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()


def get_async_database_url(database_url: str) -> str:
    """Normalize Supabase/Postgres URLs for SQLAlchemy's asyncpg driver."""
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    raise ValueError("DATABASE_URL must start with postgresql:// or postgresql+asyncpg://")


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing. Add it to Render's environment variables.")

engine = create_async_engine(
    get_async_database_url(DATABASE_URL),
    echo=False,
    pool_pre_ping=True,
    # Required for Supabase's transaction pooler when using asyncpg.
    connect_args={"statement_cache_size": 0},
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide one AsyncSession per request and clean it up safely."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
