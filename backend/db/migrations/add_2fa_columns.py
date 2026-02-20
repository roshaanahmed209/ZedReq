"""
Migration: Add 2FA columns to users table
Run this script to add two_factor_secret, two_factor_backup_codes, and two_factor_verified columns

This migration adds support for Two-Factor Authentication (2FA) using TOTP:
- two_factor_secret: Encrypted TOTP secret for authenticator apps
- two_factor_backup_codes: Encrypted backup codes for account recovery
- two_factor_verified: Flag indicating if 2FA setup is complete

Usage:
    python backend/db/migrations/add_2fa_columns.py

Rollback:
    python backend/db/migrations/add_2fa_columns.py --rollback
"""
import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
ADD_2FA_COLUMNS = '''
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS two_factor_secret TEXT,
ADD COLUMN IF NOT EXISTS two_factor_backup_codes TEXT,
ADD COLUMN IF NOT EXISTS two_factor_verified BOOLEAN DEFAULT FALSE;
'''

# Rollback SQL
DROP_2FA_COLUMNS = '''
ALTER TABLE users 
DROP COLUMN IF EXISTS two_factor_secret,
DROP COLUMN IF EXISTS two_factor_backup_codes,
DROP COLUMN IF EXISTS two_factor_verified;
'''

def check_columns_exist(db):
    """Check if 2FA columns already exist"""
    try:
        result = db.fetch_one("""
            SELECT COUNT(*) as count
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('two_factor_secret', 'two_factor_backup_codes', 'two_factor_verified')
        """)
        # Check if all 3 columns exist
        if result:
            count = result.get('count', 0) if isinstance(result, dict) else result[0] if isinstance(result, (list, tuple)) else 0
            return count >= 3
        return False
    except Exception as e:
        # If query fails, assume columns don't exist
        print(f"  [WARN] Could not check existing columns: {e}")
        return False

def run_migration(rollback=False):
    """Run the migration to add or remove 2FA columns"""
    db = Database(get_connection_params())
    
    print("=" * 60)
    if rollback:
        print("Running Migration: Remove 2FA columns from users table")
    else:
        print("Running Migration: Add 2FA columns to users table")
    print("=" * 60)
    
    try:
        if rollback:
            # Check if columns exist before dropping
            print("  [1/2] Checking if 2FA columns exist...")
            columns_exist = check_columns_exist(db)
            
            if not columns_exist:
                print("  [INFO] 2FA columns do not exist. Nothing to rollback.")
                print("=" * 60)
                print("Rollback completed (no changes needed)")
                print("=" * 60)
                return
            
            print("  [2/2] Dropping 2FA columns...")
            db.execute(DROP_2FA_COLUMNS)
            print("  [OK] 2FA columns removed successfully")
            print("=" * 60)
            print("Rollback completed successfully!")
            print("=" * 60)
        else:
            # Check if columns already exist
            print("  [1/2] Checking if 2FA columns already exist...")
            columns_exist = check_columns_exist(db)
            
            if columns_exist:
                print("  [INFO] 2FA columns already exist. Skipping migration.")
                print("=" * 60)
                print("Migration completed (no changes needed)")
                print("=" * 60)
                return
            
            print("  [2/2] Adding 2FA columns to users table...")
            db.execute(ADD_2FA_COLUMNS)
            print("  [OK] 2FA columns added successfully")
            print("=" * 60)
            print("Migration completed successfully!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Set 2FA_ENCRYPTION_KEY in your .env file")
            print("2. Install required packages: pip install pyotp qrcode[pil] cryptography")
            print("3. Restart your application")
            print("=" * 60)
            
    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add or remove 2FA columns from users table')
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback the migration (remove 2FA columns)'
    )
    args = parser.parse_args()
    
    run_migration(rollback=args.rollback)
