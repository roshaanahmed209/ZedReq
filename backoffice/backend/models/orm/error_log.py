"""Error Log ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class ErrorLog(Base):
    """SQLAlchemy ORM model for error_logs table"""
    __tablename__ = 'error_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    error_type = Column(String(100), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    endpoint = Column(String(255), index=True)
    user_id = Column(Integer)
    ip_address = Column(String(45))
    severity = Column(String(20), default='error', index=True)
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_errors_type', 'error_type', 'timestamp'),
        Index('idx_errors_severity', 'severity', 'timestamp'),
        Index('idx_errors_resolved', 'resolved', 'timestamp'),
        Index('idx_errors_timestamp', 'timestamp'),
        Index('idx_errors_endpoint', 'endpoint', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<ErrorLog(id={self.id}, type='{self.error_type}', severity='{self.severity}', resolved={self.resolved})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'stack_trace': self.stack_trace,
            'endpoint': self.endpoint,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'severity': self.severity,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
