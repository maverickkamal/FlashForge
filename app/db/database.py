from supabase import create_client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create Supabase client only if valid credentials are provided
supabase = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY and settings.SUPABASE_URL != "your-project-id.supabase.co":
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize Supabase client: {e}")
        print("Continuing with SQLite for local testing only")

# For testing, we'll use SQLite instead of PostgreSQL
# This allows us to test without Supabase credentials
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create SQLAlchemy async engine
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for all database models
Base = declarative_base()

# Database dependency function
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()