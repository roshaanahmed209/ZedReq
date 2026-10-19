"""
Migration script to convert existing full profile URLs to paths only
This fixes any URLs that were stored with the full domain (e.g., http://localhost:5000/profile/...)
and converts them to paths only (e.g., /profile/...)
"""
import os
import sys
from pathlib import Path
import re

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database_orm import get_db
from models.orm import User
from sqlalchemy import text


def fix_profile_urls_to_paths():
    """Convert full URLs to paths only"""
    db = next(get_db())
    
    try:
        print("Checking for profile URLs that need conversion...")
        users = db.query(User).filter(User.profile_url.isnot(None)).all()
        updated_count = 0
        
        for user in users:
            if user.profile_url:
                # Check if it's a full URL (starts with http:// or https://)
                if user.profile_url.startswith('http://') or user.profile_url.startswith('https://'):
                    # Extract just the path part
                    # Match pattern: http(s)://domain/path
                    match = re.search(r'https?://[^/]+(/.*)', user.profile_url)
                    if match:
                        path = match.group(1)
                        user.profile_url = path
                        updated_count += 1
                        print(f"  Updated user {user.uid}: {user.profile_url}")
                    else:
                        # If we can't parse it, try to extract /profile/... part
                        if '/profile/' in user.profile_url:
                            path = '/' + user.profile_url.split('/profile/')[1]
                            if path.startswith('/profile/'):
                                user.profile_url = path
                                updated_count += 1
                                print(f"  Updated user {user.uid}: {user.profile_url}")
        
        if updated_count > 0:
            db.commit()
            print(f"\nUpdated {updated_count} profile URLs to paths only")
        else:
            print("\nNo URLs needed conversion (all are already paths)")
        
        print("Migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    fix_profile_urls_to_paths()
