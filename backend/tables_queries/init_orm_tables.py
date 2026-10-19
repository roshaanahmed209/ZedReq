"""
Initialize ORM Tables - Creates tables from SQLAlchemy models
This script uses SQLAlchemy's metadata to create tables automatically
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_orm import engine, Base
# Import all ORM models so SQLAlchemy knows about them
# User must be imported first so other models can reference it
from models.orm import (
    User, 
    Connection, 
    ConnectionRequest, 
    Notification, 
    Post,
    Like,
    Description,
    JobPosting, 
    JobApplication, 
    JobSaved
)

def init_tables():
    """Create all ORM tables"""
    print("=" * 60)
    print("Initializing ORM Tables from SQLAlchemy Models...")
    print("=" * 60)
    
    try:
        # Create all tables defined in ORM models
        Base.metadata.create_all(bind=engine)
        print("  [OK] All tables created successfully!")
        print()
        print("Created tables:")
        print("  - users (already exists, metadata only)")
        print("  - description (already exists, metadata only)")
        print("  - connections")
        print("  - connection_requests")
        print("  - notifications")
        print("  - post")
        print("  - likes")
        print("  - job_postings")
        print("  - job_applications")
        print("  - job_saved")
        print()
        print("=" * 60)
        print("ORM Tables Initialization Complete!")
        print("=" * 60)
    except Exception as e:
        print(f"  [ERROR] Failed to create tables: {e}")
        raise


def drop_tables():
    """Drop all ORM tables (use with caution!)"""
    print("=" * 60)
    print("Dropping ORM Tables...")
    print("=" * 60)
    
    try:
        Base.metadata.drop_all(bind=engine)
        print("  [OK] All tables dropped successfully!")
        print("=" * 60)
        print("Drop Complete!")
        print("=" * 60)
    except Exception as e:
        print(f"  [ERROR] Failed to drop tables: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize ORM Tables')
    parser.add_argument('--drop', action='store_true', help='Drop all tables instead of creating')
    
    args = parser.parse_args()
    
    if args.drop:
        confirm = input("⚠️  Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == 'yes':
            drop_tables()
        else:
            print("Cancelled.")
    else:
        init_tables()
