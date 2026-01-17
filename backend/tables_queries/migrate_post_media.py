"""
Migration: Add Media Support to Posts Table
============================================
This migration updates the post table to support Cloudinary media URLs.

Changes:
    - Adds media_url (TEXT) column for Cloudinary URLs
    - Adds media_type (VARCHAR) column for 'image' or 'video'
    - Adds optimized indexes for feed queries
    - Optionally removes old media_ref_id column

Run with: python -m tables_queries.migrate_post_media
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import init_database
from utils.logger import setup_logger

logger = setup_logger(__name__)

# ============================================================================
# MIGRATION SQL STATEMENTS
# ============================================================================

# Step 1: Add new columns (if they don't exist)
ADD_MEDIA_URL_COLUMN = '''
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'post' AND column_name = 'media_url'
    ) THEN
        ALTER TABLE post ADD COLUMN media_url TEXT;
        RAISE NOTICE 'Added media_url column';
    ELSE
        RAISE NOTICE 'media_url column already exists';
    END IF;
END $$;
'''

ADD_MEDIA_TYPE_COLUMN = '''
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'post' AND column_name = 'media_type'
    ) THEN
        ALTER TABLE post ADD COLUMN media_type VARCHAR(20);
        RAISE NOTICE 'Added media_type column';
    ELSE
        RAISE NOTICE 'media_type column already exists';
    END IF;
END $$;
'''

# Step 2: Add optimized indexes for feed queries
ADD_FEED_INDEXES = [
    '''
    CREATE INDEX IF NOT EXISTS idx_post_uid_created_deleted 
    ON post(uid, created_at DESC, is_deleted);
    ''',
    '''
    CREATE INDEX IF NOT EXISTS idx_post_feed 
    ON post(created_at DESC, post_id DESC) 
    WHERE is_deleted = FALSE;
    ''',
    '''
    CREATE INDEX IF NOT EXISTS idx_post_media 
    ON post(media_url) 
    WHERE media_url IS NOT NULL;
    '''
]

# Step 3: Optional - Drop old media_ref_id column
DROP_OLD_COLUMN = '''
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'post' AND column_name = 'media_ref_id'
    ) THEN
        ALTER TABLE post DROP COLUMN media_ref_id;
        RAISE NOTICE 'Dropped old media_ref_id column';
    ELSE
        RAISE NOTICE 'media_ref_id column does not exist';
    END IF;
END $$;
'''

# Rollback: Remove new columns and restore old one
ROLLBACK_ADD_MEDIA_REF_ID = '''
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'post' AND column_name = 'media_ref_id'
    ) THEN
        ALTER TABLE post ADD COLUMN media_ref_id INTEGER;
        RAISE NOTICE 'Restored media_ref_id column';
    END IF;
END $$;
'''

ROLLBACK_DROP_NEW_COLUMNS = '''
ALTER TABLE post 
DROP COLUMN IF EXISTS media_url,
DROP COLUMN IF EXISTS media_type;
'''

ROLLBACK_DROP_INDEXES = [
    'DROP INDEX IF EXISTS idx_post_uid_created_deleted;',
    'DROP INDEX IF EXISTS idx_post_feed;',
    'DROP INDEX IF EXISTS idx_post_media;'
]


# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def check_current_schema(db):
    """Check current state of post table"""
    result = db.fetch_all('''
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'post'
        ORDER BY ordinal_position
    ''')
    
    print("\n📋 Current post table schema:")
    print("-" * 50)
    for col in result:
        print(f"  {col['column_name']:20} {col['data_type']:15} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
    print("-" * 50)
    
    return {col['column_name'] for col in result}


def run_migration(db, drop_old_column=False):
    """
    Run the migration to add media support.
    
    Args:
        db: Database connection
        drop_old_column: If True, drops the old media_ref_id column
    """
    print("\n🚀 Starting migration: Add Media Support to Posts")
    print("=" * 60)
    
    # Check current state
    existing_columns = check_current_schema(db)
    
    # Step 1: Add media_url column
    print("\n📦 Step 1: Adding media_url column...")
    try:
        db.execute(ADD_MEDIA_URL_COLUMN)
        print("  ✅ media_url column ready")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        raise
    
    # Step 2: Add media_type column
    print("\n📦 Step 2: Adding media_type column...")
    try:
        db.execute(ADD_MEDIA_TYPE_COLUMN)
        print("  ✅ media_type column ready")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        raise
    
    # Step 3: Add indexes
    print("\n📦 Step 3: Adding optimized indexes...")
    for i, index_sql in enumerate(ADD_FEED_INDEXES, 1):
        try:
            db.execute(index_sql)
            index_name = index_sql.split("EXISTS")[1].split("ON")[0].strip()
            print(f"  ✅ Index {i}: {index_name}")
        except Exception as e:
            print(f"  ⚠️  Index {i} warning: {e}")
    
    # Step 4: Optionally drop old column
    if drop_old_column and 'media_ref_id' in existing_columns:
        print("\n📦 Step 4: Dropping old media_ref_id column...")
        try:
            db.execute(DROP_OLD_COLUMN)
            print("  ✅ Old column dropped")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            raise
    else:
        print("\n📦 Step 4: Keeping media_ref_id column (use --drop-old to remove)")
    
    # Show final schema
    print("\n" + "=" * 60)
    check_current_schema(db)
    
    print("\n✅ Migration completed successfully!")
    print("\nNext steps:")
    print("  1. Restart your Flask server")
    print("  2. Test creating a post with media")
    print("  3. Verify feed displays media correctly")


def run_rollback(db):
    """Rollback the migration"""
    print("\n⏪ Rolling back migration: Remove Media Support")
    print("=" * 60)
    
    # Drop new indexes
    print("\n📦 Step 1: Dropping new indexes...")
    for index_sql in ROLLBACK_DROP_INDEXES:
        try:
            db.execute(index_sql)
            print(f"  ✅ Dropped index")
        except Exception as e:
            print(f"  ⚠️  Warning: {e}")
    
    # Drop new columns
    print("\n📦 Step 2: Dropping new columns...")
    try:
        db.execute(ROLLBACK_DROP_NEW_COLUMNS)
        print("  ✅ Dropped media_url and media_type columns")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        raise
    
    # Restore old column
    print("\n📦 Step 3: Restoring media_ref_id column...")
    try:
        db.execute(ROLLBACK_ADD_MEDIA_REF_ID)
        print("  ✅ Restored media_ref_id column")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        raise
    
    check_current_schema(db)
    print("\n✅ Rollback completed!")


def check_migration_status(db):
    """Check if migration has been applied"""
    existing_columns = check_current_schema(db)
    
    has_new_columns = 'media_url' in existing_columns and 'media_type' in existing_columns
    has_old_column = 'media_ref_id' in existing_columns
    
    print("\n📊 Migration Status:")
    print(f"  • New columns (media_url, media_type): {'✅ Present' if has_new_columns else '❌ Missing'}")
    print(f"  • Old column (media_ref_id): {'⚠️  Still present' if has_old_column else '✅ Removed'}")
    
    # Check indexes
    indexes = db.fetch_all('''
        SELECT indexname FROM pg_indexes WHERE tablename = 'post'
    ''')
    index_names = {idx['indexname'] for idx in indexes}
    
    print("\n📊 Indexes:")
    for idx in ['idx_post_uid_created_deleted', 'idx_post_feed', 'idx_post_media']:
        status = '✅' if idx in index_names else '❌'
        print(f"  • {idx}: {status}")
    
    return has_new_columns


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migration: Add Media Support to Posts Table',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python -m tables_queries.migrate_post_media              # Run migration
  python -m tables_queries.migrate_post_media --status     # Check status
  python -m tables_queries.migrate_post_media --drop-old   # Run and drop old column
  python -m tables_queries.migrate_post_media --rollback   # Undo migration
        '''
    )
    
    parser.add_argument(
        '--status', 
        action='store_true', 
        help='Check migration status without making changes'
    )
    parser.add_argument(
        '--drop-old', 
        action='store_true', 
        help='Drop the old media_ref_id column after migration'
    )
    parser.add_argument(
        '--rollback', 
        action='store_true', 
        help='Rollback the migration (remove new columns, restore old)'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    args = parser.parse_args()
    
    # Initialize database
    print("🔌 Connecting to database...")
    db = init_database()
    
    try:
        if args.status:
            # Just check status
            check_migration_status(db)
        
        elif args.rollback:
            # Rollback migration
            if not args.yes:
                confirm = input("\n⚠️  This will remove media_url and media_type columns. Continue? [y/N]: ")
                if confirm.lower() != 'y':
                    print("Cancelled.")
                    sys.exit(0)
            run_rollback(db)
        
        else:
            # Run migration
            if not args.yes:
                print("\nThis migration will:")
                print("  • Add media_url (TEXT) column")
                print("  • Add media_type (VARCHAR) column")
                print("  • Add optimized indexes for feed queries")
                if args.drop_old:
                    print("  • DROP the old media_ref_id column")
                
                confirm = input("\nContinue? [y/N]: ")
                if confirm.lower() != 'y':
                    print("Cancelled.")
                    sys.exit(0)
            
            run_migration(db, drop_old_column=args.drop_old)
    
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
    
    finally:
        db.close()
