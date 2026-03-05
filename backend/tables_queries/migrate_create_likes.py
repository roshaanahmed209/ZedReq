"""
Migration: Create Likes Table
==============================
Creates the likes table for post likes functionality.

Run with: python -m tables_queries.migrate_create_likes
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import init_database

# ============================================================================
# MIGRATION SQL
# ============================================================================

CREATE_LIKES_TABLE = '''
CREATE TABLE IF NOT EXISTS likes (
    like_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES post(post_id) ON DELETE CASCADE,
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, uid)
);
'''

CREATE_LIKES_INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_likes_post ON likes(post_id);',
    'CREATE INDEX IF NOT EXISTS idx_likes_user ON likes(uid);',
    'CREATE INDEX IF NOT EXISTS idx_likes_post_user ON likes(post_id, uid);'
]


def run_migration():
    """Create the likes table"""
    print("[*] Connecting to database...")
    db = init_database()
    
    print("\n[*] Creating likes table...")
    print("=" * 50)
    
    try:
        # Create table
        db.execute(CREATE_LIKES_TABLE)
        print("  [OK] Created likes table")
        
        # Create indexes
        for index_sql in CREATE_LIKES_INDEXES:
            db.execute(index_sql)
            index_name = index_sql.split("EXISTS")[1].split("ON")[0].strip()
            print(f"  [OK] Created index: {index_name}")
        
        print("\n" + "=" * 50)
        print("[OK] Migration completed successfully!")
        print("\nThe likes table is now ready.")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
