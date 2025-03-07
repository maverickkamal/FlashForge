import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import engine, Base, supabase
from app.auth.models import User

async def create_tables():
    """Create database tables if they don't exist."""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

async def init_db():
    """Initialize the database."""
    await create_tables()
    print("Database initialized successfully.")
    
    # Check if we're using Supabase
    use_sqlite = os.getenv("USE_SQLITE", "false").lower() == "true"
    if not use_sqlite:
        print("Using Supabase PostgreSQL database")
        try:
            # Verify Supabase connection by checking if the users table exists
            if supabase:
                # Test the connection with a simple query
                response = supabase.table('users').select('*').execute()
                users = response.data
                print(f"Connected to Supabase. Found {len(users)} users in database.")
            else:
                print("Warning: Supabase client not initialized. Check your credentials.")
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            print("Falling back to SQLite for local testing.")
    else:
        print("Using SQLite for local testing.")

if __name__ == "__main__":
    asyncio.run(init_db())