import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("[-] Error: DATABASE_URL is missing in .env")

# Convert the standard Postgres URI to the asyncpg driver URI
ASYNC_DB_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create the async database engine
# Note: statement_cache_size=0 is critical when using port 6543 (Transaction Pooler)
engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    connect_args={"statement_cache_size": 0}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session