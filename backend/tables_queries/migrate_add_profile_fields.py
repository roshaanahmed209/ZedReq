"""
Migration: Add location and industry fields to description table
Run this script to add the new columns to existing databases
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_database

# SQL to add new columns
ADD_LOCATION_COLUMN = '''
ALTER TABLE description 
ADD COLUMN IF NOT EXISTS location VARCHAR(150);
'''

ADD_INDUSTRY_COLUMN = '''
ALTER TABLE description 
ADD COLUMN IF NOT EXISTS industry VARCHAR(100);
'''

ADD_ROLE_COLUMN = '''
ALTER TABLE description 
ADD COLUMN IF NOT EXISTS role VARCHAR(150);
'''

ADD_COMPANY_COLUMN = '''
ALTER TABLE description 
ADD COLUMN IF NOT EXISTS company VARCHAR(150);
'''

def migrate():
    """Add location and industry columns to description table"""
    db = get_database()
    if not db:
        print("Error: Could not connect to database")
        return False
    
    try:
        print("Adding location column to description table...")
        db.execute(ADD_LOCATION_COLUMN)
        
        print("Adding industry column to description table...")
        db.execute(ADD_INDUSTRY_COLUMN)
        
        print("Adding role column to description table...")
        db.execute(ADD_ROLE_COLUMN)
        
        print("Adding company column to description table...")
        db.execute(ADD_COMPANY_COLUMN)
        
        print("Migration completed successfully!")
        return True
    except Exception as e:
        print(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    migrate()
