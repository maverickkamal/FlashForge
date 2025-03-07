import asyncio
import requests
from supabase import create_client
from app.config import settings

# SQL to create the proper table schema
SQL_CREATE_SCHEMA = """
-- Drop tables if they exist (careful with this in production!)
DROP TABLE IF EXISTS flashcards;
DROP TABLE IF EXISTS decks;
DROP TABLE IF EXISTS users;

-- Create users table with the correct schema
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Create decks table
CREATE TABLE IF NOT EXISTS decks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE
);

-- Create flashcards table
CREATE TABLE IF NOT EXISTS flashcards (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE
);
"""

async def initialize_supabase():
    """Initialize the Supabase database with the correct schema."""
    print("Initializing Supabase database...")
    
    # Initialize Supabase client
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print(f"Connected to Supabase at {settings.SUPABASE_URL}")
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return False
    
    # Execute SQL directly using Supabase REST API since the RPC method might not be available
    try:
        # We'll use the direct PostgreSQL REST API provided by Supabase
        # This requires using the service_role key which has higher privileges
        # Extract project reference from URL
        project_ref = settings.SUPABASE_URL.split('//')[1].split('.')[0]
        
        print("The SQL to create tables needs to be executed manually in the Supabase SQL Editor.")
        print("Please follow these steps:")
        print("1. Go to https://app.supabase.com")
        print("2. Select your project")
        print("3. Go to the SQL Editor")
        print("4. Copy and paste the following SQL and execute it:")
        print("\n" + SQL_CREATE_SCHEMA)
        
        # Ask user if they've executed the SQL
        print("\nHave you executed the SQL in the Supabase SQL Editor? (y/n)")
        user_input = input().lower()
        
        if user_input != 'y':
            print("Please execute the SQL before continuing.")
            return False
            
        # Check if tables were created correctly
        try:
            print("\nVerifying table structure...")
            response = supabase.table('users').select('*').limit(1).execute()
            print("✅ Users table exists and is accessible.")
        except Exception as e:
            print(f"❌ Error accessing users table: {e}")
            return False
            
        print("\nDatabase initialization completed successfully.")
        return True
        
    except Exception as e:
        print(f"Error initializing Supabase database: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(initialize_supabase())
    
    if success:
        print("\nNow you can run the migration script to transfer existing users:")
        print("python migrate_users_to_supabase.py")
    else:
        print("\nDatabase initialization failed. Please fix the issues and try again.")