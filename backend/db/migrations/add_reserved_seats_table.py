"""
Migration: Create reserved_seats table
- Stores email reservations for early access
- Generates unique promo codes
- Links to users table (optional)
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
CREATE_RESERVED_SEATS_TABLE = '''
CREATE TABLE IF NOT EXISTS reserved_seats (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    user_id INTEGER REFERENCES users(uid) ON DELETE SET NULL,
    promo_code VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

CREATE_RESERVED_SEATS_INDEXES = '''
CREATE INDEX IF NOT EXISTS idx_reserved_seats_email 
ON reserved_seats(email);

CREATE INDEX IF NOT EXISTS idx_reserved_seats_user_id 
ON reserved_seats(user_id) 
WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_reserved_seats_promo_code 
ON reserved_seats(promo_code);

CREATE INDEX IF NOT EXISTS idx_reserved_seats_created_at 
ON reserved_seats(created_at);
'''

def run_migration():
    """Run the migration to create reserved_seats table"""
    db = Database(get_connection_params())
    
    print("=" * 60)
    print("Running Migration: Create reserved_seats table")
    print("=" * 60)
    
    try:
        # Create table
        print("  [1/2] Creating reserved_seats table...")
        db.execute(CREATE_RESERVED_SEATS_TABLE)
        print("  [OK] reserved_seats table created")
        
        # Create indexes
        print("  [2/2] Creating indexes...")
        db.execute(CREATE_RESERVED_SEATS_INDEXES)
        print("  [OK] Indexes created")
        
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
