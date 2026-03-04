"""Database connection and utilities for PostgreSQL - Backoffice specific"""
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from contextlib import contextmanager
from dotenv import load_dotenv

# Load .env from backoffice root
_backoffice_root = Path(__file__).parent.parent.parent
_env_file = _backoffice_root / ".env"
load_dotenv(_env_file)

# Try psycopg3 first, fall back to psycopg2
try:
    import psycopg
    from psycopg.rows import dict_row
    try:
        from psycopg_pool import ConnectionPool
    except ImportError:
        ConnectionPool = None  # ConnectionPool not available
    PSYCOPG_VERSION = 3
except ImportError:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    ConnectionPool = None  # ConnectionPool not available in psycopg2
    PSYCOPG_VERSION = 2


def get_connection_params() -> Dict[str, Any]:
    """Get database connection parameters from backoffice environment"""
    # Check for BACKOFFICE_DATABASE_URL first
    database_url = os.environ.get('BACKOFFICE_DATABASE_URL')
    if database_url:
        return {'conninfo': database_url}
    
    return {
        'host': os.environ.get('BACKOFFICE_DB_HOST', 'localhost'),
        'port': int(os.environ.get('BACKOFFICE_DB_PORT', 5432)),
        'dbname': os.environ.get('BACKOFFICE_DB_NAME', 'zedreq_backoffice'),
        'user': os.environ.get('BACKOFFICE_DB_USER', 'postgres'),
        'password': os.environ.get('BACKOFFICE_DB_PASSWORD', ''),
    }


class Database:
    """Database wrapper for PostgreSQL connections"""
    
    def __init__(self, params: Dict[str, Any] = None):
        self.params = params or get_connection_params()
        self._conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        if PSYCOPG_VERSION == 3:
            if 'conninfo' in self.params:
                self._conn = psycopg.connect(self.params['conninfo'], row_factory=dict_row)
            else:
                self._conn = psycopg.connect(
                    host=self.params['host'],
                    port=self.params['port'],
                    dbname=self.params['dbname'],
                    user=self.params['user'],
                    password=self.params['password'],
                    row_factory=dict_row
                )
        else:
            if 'conninfo' in self.params:
                self._conn = psycopg2.connect(self.params['conninfo'])
            else:
                self._conn = psycopg2.connect(**self.params)
        
        self._conn.autocommit = True
    
    @property
    def conn(self):
        """Get connection, reconnecting if necessary"""
        if self._conn is None or (hasattr(self._conn, 'closed') and self._conn.closed):
            self._connect()
        return self._conn
    
    def execute(self, query: str, params: tuple = None):
        """Execute a query and return cursor"""
        if PSYCOPG_VERSION == 3:
            cursor = self.conn.execute(query, params)
        else:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
        return cursor
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute query and fetch one result"""
        cursor = self.execute(query, params)
        result = cursor.fetchone()
        if PSYCOPG_VERSION == 2:
            cursor.close()
        return dict(result) if result else None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute query and fetch all results"""
        cursor = self.execute(query, params)
        results = cursor.fetchall()
        if PSYCOPG_VERSION == 2:
            cursor.close()
        return [dict(row) for row in results]
    
    def execute_returning(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute query with RETURNING clause and fetch result"""
        return self.fetch_one(query, params)
    
    def close(self):
        """Close database connection"""
        if self._conn:
            self._conn.close()
            self._conn = None


# Connection pool for production use
_pool: Optional[ConnectionPool] = None


def get_pool() -> Optional[ConnectionPool]:
    """Get or create connection pool"""
    if ConnectionPool is None:
        return None  # ConnectionPool not available
    
    global _pool
    if _pool is None:
        params = get_connection_params()
        min_size = int(os.environ.get('BACKOFFICE_DB_POOL_MIN', 5))
        max_size = int(os.environ.get('BACKOFFICE_DB_POOL_SIZE', 20))
        
        if 'conninfo' in params:
            conninfo = params['conninfo']
        else:
            conninfo = f"host={params['host']} port={params['port']} dbname={params['dbname']} user={params['user']} password={params['password']}"
        
        _pool = ConnectionPool(conninfo, min_size=min_size, max_size=max_size)
    return _pool


@contextmanager
def get_db_connection():
    """Context manager for getting a pooled database connection"""
    pool = get_pool()
    if pool is None:
        # Fallback to direct connection if pool not available
        db = Database()
        try:
            yield db.conn
        finally:
            db.close()
    else:
        conn = pool.getconn()
        try:
            yield conn
        finally:
            pool.putconn(conn)


# Global database instance for simple usage
_db: Optional[Database] = None


def init_database() -> Database:
    """Initialize and return global database instance"""
    global _db
    if _db is None:
        _db = Database()
    return _db


def get_database() -> Database:
    """Get the global database instance"""
    global _db
    if _db is None:
        _db = init_database()
    return _db
