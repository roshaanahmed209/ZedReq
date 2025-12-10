import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """Create database connection"""
        try:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
            return self._connection
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        if self._connection is None:
            self.connect()
        try:
            yield self._connection
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if self._connection:
                self._connection.rollback()
            raise
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch one row"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute query with multiple parameter sets"""
        with self.get_connection() as conn:
            conn.executemany(query, params_list)
            conn.commit()
    
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

def init_database(db_path: str):
    """Initialize database schema"""
    db = Database(db_path)
    
    with db.get_connection() as conn:
        # Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                headline TEXT,
                bio TEXT,
                avatar TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Posts table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Connections table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user1_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (user2_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user1_id, user2_id)
            )
        ''')
        
        # Likes table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(post_id, user_id)
            )
        ''')
        
        # Create indexes
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_likes_post_id ON likes(post_id)',
            'CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_connections_user1 ON connections(user1_id)',
            'CREATE INDEX IF NOT EXISTS idx_connections_user2 ON connections(user2_id)',
            'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)',
            'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)'
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
        
        conn.commit()
        logger.info("Database initialized successfully")
    
    return db
