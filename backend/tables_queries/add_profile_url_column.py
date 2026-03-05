"""
Migration script to add profile_url column to users table
Run this script to add the profile_url column and populate it for existing users
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database_orm import get_db
from models.orm import User
from utils.profile_url import generate_profile_url
from sqlalchemy import text


def add_profile_url_column():
    """Add profile_url column to users table and populate it"""
    db = next(get_db())
    
    try:
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='profile_url'
        """)
        result = db.execute(check_query).fetchone()
        
        if result:
            print("Column 'profile_url' already exists in users table")
        else:
            # Add the column
            print("Adding profile_url column to users table...")
            db.execute(text("ALTER TABLE users ADD COLUMN profile_url TEXT"))
            db.commit()
            print("Column added successfully")
        
        # Populate profile_path (not full URL) for existing users
        print("Populating profile_url (path only) for existing users...")
        from utils.profile_url import generate_profile_path
        users = db.query(User).all()
        updated_count = 0
        
        for user in users:
            if not user.profile_url and user.username:
                profile_path = generate_profile_path(user.uid, user.username)
                if profile_path:
                    user.profile_url = profile_path  # Store only path, not full URL
                    updated_count += 1
        
        db.commit()
        print(f"Updated profile_url for {updated_count} users")
        
        print("Migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_profile_url_column()
