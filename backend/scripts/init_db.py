import asyncio
import sys
from pathlib import Path

# Ensure Python can find the database.py and models.py files
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database import engine
from models import Base

async def init_models():
    async with engine.begin() as conn:
        print("[+] Creating database tables in Supabase...")
        await conn.run_sync(Base.metadata.create_all)
        print("[+] Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_models())