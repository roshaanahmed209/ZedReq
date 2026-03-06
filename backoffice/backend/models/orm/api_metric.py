"""API Metric ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class APIMetric(Base):
    """SQLAlchemy ORM model for api_metrics table"""
    __tablename__ = 'api_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False, index=True)
    response_time_ms = Column(Integer, nullable=False)
    user_id = Column(Integer, index=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    error_message = Column(Text)
    
    __table_args__ = (
        Index('idx_api_endpoint', 'endpoint', 'timestamp'),
        Index('idx_api_status', 'status_code', 'timestamp'),
        Index('idx_api_timestamp', 'timestamp'),
        Index('idx_api_user', 'user_id', 'timestamp'),
        Index('idx_api_method', 'method', 'endpoint'),
    )
    
    def __repr__(self):
        return f"<APIMetric(id={self.id}, endpoint='{self.endpoint}', method='{self.method}', status={self.status_code}, time={self.response_time_ms}ms)>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'error_message': self.error_message,
        }
