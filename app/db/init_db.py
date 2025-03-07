import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import engine, Base
from app.auth.models import User

async def create_tables():
    """Create database tables if they don't exist."""
    async with engine.begin() as conn:
        # Drop all tables for clean testing (remove this in production)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

async def init_db():
    """Initialize the database."""
    await create_tables()
    print("Database initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())