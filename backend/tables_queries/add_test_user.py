"""
Add test user to database
Run: python add_test_user.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import init_database
from utils.auth import hash_password

def add_test_user():
    """Add test admin user"""
    db = init_database()
    
    # User details
    username = "roshaan"
    email = "admin@roshaan.com"
    password = "roshaan67!"
    full_name = "Roshaan Admin"
    
    # Check if user already exists
    existing = db.fetch_one(
        "SELECT uid FROM users WHERE user_email = %s OR username = %s",
        (email, username)
    )
    
    if existing:
        print(f"[X] User already exists with ID: {existing['uid']}")
        print(f"    Email: {email}")
        print(f"    Username: {username}")
        return
    
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
        print("[OK] Test user created successfully!")
        print(f"    ID: {result['uid']}")
        print(f"    Username: {result['username']}")
        print(f"    Email: {result['user_email']}")
        print(f"    Password: {password}")
        print("")
        print("You can now login with:")
        print(f"    Username: {username}  OR  Email: {email}")
        print(f"    Password: {password}")
    else:
        print("[X] Failed to create user")

if __name__ == "__main__":
    add_test_user()
