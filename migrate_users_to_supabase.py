import asyncio
import sqlite3
import json
from supabase import create_client
from app.config import settings

async def migrate_users_to_supabase():
    """Transfer users from local SQLite database to Supabase."""
    print("\nMigrating users from SQLite to Supabase...")
    
    # Initialize Supabase client
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return False
        
    # Connect to SQLite database
    try:
        conn = sqlite3.connect("test.db")
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Query all users from SQLite
        cursor.execute("SELECT id, email, hashed_password, is_active, is_superuser, is_verified FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the local SQLite database to migrate.")
            return False
        
        print(f"Found {len(users)} users in SQLite to migrate.")
        
        # Transfer each user to Supabase
        for user in users:
            user_dict = {key: user[key] for key in user.keys()}
            
            # Check if user already exists in Supabase
            response = supabase.table('users').select('*').eq('email', user_dict['email']).execute()
            
            if response.data and len(response.data) > 0:
                print(f"User {user_dict['email']} already exists in Supabase, skipping.")
                continue
                
            # Insert user into Supabase
            try:
                response = supabase.table('users').insert(user_dict).execute()
                print(f"User {user_dict['email']} successfully migrated to Supabase.")
            except Exception as e:
                print(f"Error inserting user {user_dict['email']} to Supabase: {e}")
        
        print("\nMigration completed. Verifying results:")
        response = supabase.table('users').select('*').execute()
        print(f"Total users in Supabase after migration: {len(response.data)}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    except Exception as e:
        print(f"Error during migration: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    result = asyncio.run(migrate_users_to_supabase())
    
    if result:
        print("\nDo you want to check users in Supabase now? (y/n):")
        if input().lower() == 'y':
            from check_users import check_supabase_users
            asyncio.run(check_supabase_users())
    else:
        print("\nMigration failed or no users to migrate.")