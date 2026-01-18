"""
Migration Script: Create Network Tables
Creates:
- Updated users table with UUID
- connections table (bidirectional connections)
- connection_requests table
- notifications table
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# MIGRATION SQL
# ============================================================================

ENABLE_UUID_EXTENSION = '''
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
'''

# Updated users table with UUID
USERS_TABLE_UUID = '''
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    profile_pic TEXT,
    bio TEXT,
    skills TEXT[],
    job_title VARCHAR(100),
    company VARCHAR(100),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

# Connections table (accepted connections)
CONNECTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS connections (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    connected_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, connected_user_id)
);
'''

# Connection requests table
CONNECTION_REQUESTS_TABLE = '''
CREATE TABLE IF NOT EXISTS connection_requests (
    id SERIAL PRIMARY KEY,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sender_id, receiver_id)
);
'''

# Notifications table
NOTIFICATIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    related_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    related_request_id INTEGER REFERENCES connection_requests(id) ON DELETE SET NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

# Indexes
INDEXES = [
    # Users indexes
    'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
    'CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)',
    'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)',
    
    # Connections indexes
    'CREATE INDEX IF NOT EXISTS idx_connections_user ON connections(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_connections_connected ON connections(connected_user_id)',
    
    # Connection requests indexes
    'CREATE INDEX IF NOT EXISTS idx_connection_requests_sender ON connection_requests(sender_id)',
    'CREATE INDEX IF NOT EXISTS idx_connection_requests_receiver ON connection_requests(receiver_id)',
    'CREATE INDEX IF NOT EXISTS idx_connection_requests_status ON connection_requests(status)',
    
    # Notifications indexes
    'CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE',
]


def get_db():
    """Get database connection"""
    from config.database import get_connection_params, Database
    params = get_connection_params()
    return Database(params)


def run_migration(db=None):
    """Run the migration to create network tables"""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    print("=" * 60)
    print("Running Network Tables Migration")
    print("=" * 60)
    
    try:
        # Enable UUID extension
        print("\n[1/5] Enabling UUID extension...")
        db.execute(ENABLE_UUID_EXTENSION)
        print("  [OK] UUID extension enabled")
        
        # Create users table (if not exists)
        print("\n[2/5] Creating users table...")
        db.execute(USERS_TABLE_UUID)
        print("  [OK] Users table ready")
        
        # Create connections table
        print("\n[3/5] Creating connections table...")
        db.execute(CONNECTIONS_TABLE)
        print("  [OK] Connections table created")
        
        # Create connection_requests table
        print("\n[4/5] Creating connection_requests table...")
        db.execute(CONNECTION_REQUESTS_TABLE)
        print("  [OK] Connection requests table created")
        
        # Create notifications table
        print("\n[5/5] Creating notifications table...")
        db.execute(NOTIFICATIONS_TABLE)
        print("  [OK] Notifications table created")
        
        # Create indexes
        print("\n[Indexes] Creating indexes...")
        for index_sql in INDEXES:
            try:
                db.execute(index_sql)
                index_name = index_sql.split("EXISTS")[1].split("ON")[0].strip()
                print(f"  [OK] Created index: {index_name}")
            except Exception as e:
                print(f"  [WARN] Index creation: {e}")
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        if close_db:
            db.close()


def drop_network_tables(db=None):
    """Drop network tables (for development reset)"""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    print("Dropping network tables...")
    
    try:
        # Drop in reverse order of dependencies
        db.execute("DROP TABLE IF EXISTS notifications CASCADE")
        print("  [OK] Dropped notifications table")
        
        db.execute("DROP TABLE IF EXISTS connection_requests CASCADE")
        print("  [OK] Dropped connection_requests table")
        
        db.execute("DROP TABLE IF EXISTS connections CASCADE")
        print("  [OK] Dropped connections table")
        
        print("Network tables dropped successfully!")
        
    except Exception as e:
        print(f"[ERROR] Failed to drop tables: {e}")
    finally:
        if close_db:
            db.close()


def get_migration_sql():
    """Get all migration SQL as a single string"""
    sql_parts = [
        "-- Network Tables Migration",
        "-- Run this SQL to create the network feature tables\n",
        "-- Enable UUID extension",
        ENABLE_UUID_EXTENSION,
        "\n-- Users table (UUID primary key)",
        USERS_TABLE_UUID,
        "\n-- Connections table",
        CONNECTIONS_TABLE,
        "\n-- Connection Requests table",
        CONNECTION_REQUESTS_TABLE,
        "\n-- Notifications table",
        NOTIFICATIONS_TABLE,
        "\n-- Indexes",
    ]
    
    for index_sql in INDEXES:
        sql_parts.append(f"{index_sql};")
    
    return "\n".join(sql_parts)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Network tables migration')
    parser.add_argument('--drop', action='store_true', help='Drop network tables')
    parser.add_argument('--print-sql', action='store_true', help='Print SQL instead of executing')
    
    args = parser.parse_args()
    
    if args.print_sql:
        print(get_migration_sql())
    elif args.drop:
        drop_network_tables()
    else:
        run_migration()
