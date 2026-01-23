"""
Add 20 test users to database
Run: python add_20_users.py
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the backend directory path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from backend/.env before importing config
env_path = Path(backend_dir) / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"Warning: .env file not found at {env_path}")
    print("Attempting to load from current directory...")
    load_dotenv()

# Add parent directory (backend) to path for imports
sys.path.insert(0, backend_dir)

from config.database import init_database
from utils.auth import hash_password

# Number words for passwords
NUMBER_WORDS = [
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 
    'eighteen', 'nineteen', 'twenty'
]

def add_20_users():
    """Add 20 test users to the database"""
    db = init_database()
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    print("=" * 60)
    print("Adding 20 users to database...")
    print("=" * 60)
    print()
    
    for i in range(1, 21):
        # User details
        username = f"user{i}"
        email = f"user{i}@mail.com"
        password = f"User{NUMBER_WORDS[i-1]}"
        full_name = f"User {NUMBER_WORDS[i-1].capitalize()}"
        
        # Check if user already exists
        existing = db.fetch_one(
            "SELECT uid FROM users WHERE user_email = %s OR username = %s",
            (email, username)
        )
        
        if existing:
            print(f"[SKIP] User {i:2d}: {username} already exists (ID: {existing['uid']})")
            skipped_count += 1
            continue
        
        try:
            # Hash password
            password_hash = hash_password(password)
            
            # Insert user
            result = db.execute_returning(
                """INSERT INTO users (username, name, user_email, password_hash, email_verified)
                   VALUES (%s, %s, %s, %s, TRUE)
                   RETURNING uid, username, user_email""",
                (username, full_name, email, password_hash)
            )
            
            if result:
                created_count += 1
                print(f"[OK] User {i:2d}: {username:8s} | {email:20s} | Password: {password}")
            else:
                error_count += 1
                print(f"[ERROR] User {i:2d}: Failed to create {username}")
        except Exception as e:
            error_count += 1
            print(f"[ERROR] User {i:2d}: {username} - {str(e)}")
    
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Created: {created_count}")
    print(f"  Skipped: {skipped_count} (already exist)")
    print(f"  Errors:  {error_count}")
    print("=" * 60)
    print()
    
    if created_count > 0:
        print("Users can now login with:")
        print("  Email format: user1@mail.com, user2@mail.com, etc.")
        print("  Password format: Userone, Usertwo, Userthree, etc.")
        print()

if __name__ == "__main__":
    add_20_users()
