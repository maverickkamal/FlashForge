import asyncio
from supabase import create_client
from app.config import settings

# SQL schema for creating tables
SQL_SCHEMA = """
-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Create decks table if it doesn't exist
CREATE TABLE IF NOT EXISTS decks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE
);

-- Create flashcards table if it doesn't exist
CREATE TABLE IF NOT EXISTS flashcards (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE
);
"""

async def setup_supabase_tables():
    """Initialize Supabase database tables according to the schema."""
    print("Setting up Supabase database tables...")
    
    try:
        # Initialize Supabase client
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        # First try to check if tables exist by selecting from them
        try:
            response = supabase.table('users').select('id').limit(1).execute()
            print("Users table exists.")
        except Exception as e:
            print(f"Users table might not exist: {e}")
            print("Will attempt to create tables...")
        
        # Use Supabase SQL to create tables
        try:
            # Note: This requires appropriate permissions in Supabase
            # You might need to execute this SQL manually in the Supabase SQL editor
            response = supabase.rpc('exec_sql', {'query': SQL_SCHEMA}).execute()
            print("SQL execution completed.")
        except Exception as e:
            print(f"Error executing SQL: {e}")
            print("You'll need to create tables manually in the Supabase SQL Editor.")
            print("Use this SQL Schema:")
            print(SQL_SCHEMA)
        
        # Check tables after creation
        print("\nChecking tables status:")
        try:
            users = supabase.table('users').select('*').execute()
            print(f"Users table has {len(users.data)} records")
        except Exception as e:
            print(f"Error checking users table: {e}")
        
        try:
            decks = supabase.table('decks').select('*').execute()
            print(f"Decks table has {len(decks.data)} records")
        except Exception as e:
            print(f"Error checking decks table: {e}")
            
        try:
            flashcards = supabase.table('flashcards').select('*').execute()
            print(f"Flashcards table has {len(flashcards.data)} records")
        except Exception as e:
            print(f"Error checking flashcards table: {e}")
        
    except Exception as e:
        print(f"Error setting up Supabase: {e}")
        print("You may need to manually create tables in the Supabase SQL editor.")

if __name__ == "__main__":
    asyncio.run(setup_supabase_tables())