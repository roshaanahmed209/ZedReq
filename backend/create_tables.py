"""Create missing tables for the network feature"""
from config.database import get_database, init_database

def create_tables():
    init_database()
    db = get_database()
    
    # Check and create connection_requests table
    result = db.fetch_one("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'connection_requests'
        )
    """)
    
    if not result or not result['exists']:
        print("Creating connection_requests table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS connection_requests (
                id SERIAL PRIMARY KEY,
                sender_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
                receiver_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
                status VARCHAR(20) DEFAULT 'pending',
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sender_id, receiver_id)
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_conn_req_sender ON connection_requests(sender_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_conn_req_receiver ON connection_requests(receiver_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_conn_req_status ON connection_requests(status)")
        print("connection_requests table created!")
    else:
        print("connection_requests table already exists")
    
    # Check and create notifications table
    result = db.fetch_one("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'notifications'
        )
    """)
    
    if not result or not result['exists']:
        print("Creating notifications table...")
        db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
                notification_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                related_user_id INTEGER REFERENCES users(uid) ON DELETE SET NULL,
                related_request_id INTEGER REFERENCES connection_requests(id) ON DELETE SET NULL,
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_notif_unread ON notifications(user_id, is_read) WHERE is_read = FALSE")
        print("notifications table created!")
    else:
        print("notifications table already exists")
    
    print("Done!")

if __name__ == "__main__":
    create_tables()
