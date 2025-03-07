from supabase import create_client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import socket
from urllib.parse import quote_plus

from app.config import settings

# Create Supabase client for API operations
supabase = None
supabase_connected = False

# Try to establish Supabase API connection
if settings.SUPABASE_URL and settings.SUPABASE_KEY and "your-project-id" not in settings.SUPABASE_URL:
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        # Test connection with a simple call
        test_response = supabase.from_("users").select("*", count="exact").limit(1).execute()
        supabase_connected = True
        print(f"Successfully connected to Supabase API at {settings.SUPABASE_URL}")
    except Exception as e:
        print(f"Warning: Could not initialize Supabase client: {e}")

# Always use SQLite for SQLAlchemy operations to avoid DNS resolution issues
# While using Supabase API for actual data operations
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
print("Using SQLite database for local ORM operations")

# Create SQLAlchemy engine with basic configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

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