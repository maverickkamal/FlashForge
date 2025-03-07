import asyncio
import sqlite3
import json
import os
from supabase import create_client
from app.config import settings

async def check_supabase_users():
    """Check users directly in Supabase database."""
    print("\nChecking Supabase users...")
    
    try:
        # Initialize Supabase client
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        # Query users from the 'users' table
        response = supabase.table('users').select('id, email, is_active, is_superuser, is_verified').execute()
        users = response.data
        
        if not users:
            print("No users found in Supabase database.")
            return
        
        print(f"Found {len(users)} users in Supabase database:")
        print("-" * 80)
        
        # Print user information
        for user in users:
            print(json.dumps(user, indent=2))
            print("-" * 40)
            
    except Exception as e:
        print(f"Supabase error: {e}")
        print("Failed to connect to Supabase. You can:")
        print("1. Check your SUPABASE_URL and SUPABASE_KEY in .env file")
        print("2. Ensure the 'users' table exists in your Supabase project")
        print("3. Try checking local SQLite database instead")

async def check_local_users():
    """Check all users in the local SQLite database."""
    print("\nChecking local SQLite users...")
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect("test.db")
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Query all users
        cursor.execute("SELECT id, email, is_active, is_superuser, is_verified FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the local SQLite database.")
            return
        
        print(f"Found {len(users)} users in the local SQLite database:")
        print("-" * 80)
        
        # Print user information
        for user in users:
            user_dict = {key: user[key] for key in user.keys()}
            print(json.dumps(user_dict, indent=2))
            print("-" * 40)
            
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

def print_supabase_management_info():
    """Print information about managing users in Supabase dashboard."""
    print("\n=== MANAGING USERS IN SUPABASE DASHBOARD ===\n")
    print("To view and manage users in your Supabase dashboard:")
    print("1. Go to https://app.supabase.com and log in")
    print("2. Select your project (xbehioydvwazjptbtuwe)")
    print("3. Go to the 'Authentication' section in the left sidebar")
    print("4. Select the 'Users' tab to view and manage all users")
    print("\nTo view raw database entries:")
    print("1. Go to the 'Table Editor' section in the left sidebar")
    print("2. Select the 'users' table to view all database records")
    print("\nTo run SQL queries:")
    print("1. Go to the 'SQL Editor' section in the left sidebar")
    print("2. Run a query like:")
    print("   SELECT * FROM users;")

if __name__ == "__main__":
    # Determine which database to check
    use_sqlite = os.getenv("USE_SQLITE", "false").lower() == "true"
    
    if not use_sqlite:
        # Default to checking Supabase first
        asyncio.run(check_supabase_users())
    
    # Always provide SQLite option as backup
    if use_sqlite or input("\nDo you want to check local SQLite database too? (y/n): ").lower() == 'y':
        asyncio.run(check_local_users())
    
    # Always print management info
    print_supabase_management_info()