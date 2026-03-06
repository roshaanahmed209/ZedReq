"""Database Metric ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class DatabaseMetric(Base):
    """SQLAlchemy ORM model for database_metrics table"""
    __tablename__ = 'database_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    query_time_ms = Column(Numeric(10, 2))
    slow_queries_count = Column(Integer, default=0)
    connection_pool_usage = Column(Integer, default=0)
    active_connections = Column(Integer, default=0)
    database_size_mb = Column(Numeric(10, 2))
    replication_lag_ms = Column(Integer)
    database_name = Column(String(100), default='main', index=True)
    
    __table_args__ = (
        Index('idx_dbmetrics_timestamp', 'timestamp'),
        Index('idx_dbmetrics_dbname', 'database_name', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<DatabaseMetric(id={self.id}, db='{self.database_name}', timestamp={self.timestamp})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'query_time_ms': float(self.query_time_ms) if self.query_time_ms else None,
            'slow_queries_count': self.slow_queries_count,
            'connection_pool_usage': self.connection_pool_usage,
            'active_connections': self.active_connections,
            'database_size_mb': float(self.database_size_mb) if self.database_size_mb else None,
            'replication_lag_ms': self.replication_lag_ms,
            'database_name': self.database_name,
        }
