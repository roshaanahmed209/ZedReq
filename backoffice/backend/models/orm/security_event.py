"""Security Event ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from config.database_orm import Base


class SecurityEvent(Base):
    """SQLAlchemy ORM model for security_events table"""
    __tablename__ = 'security_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, index=True)
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    details = Column(JSONB)
    severity = Column(String(20), default='medium', index=True)
    blocked = Column(Boolean, default=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_security_type', 'event_type', 'timestamp'),
        Index('idx_security_user', 'user_id', 'timestamp'),
        Index('idx_security_ip', 'ip_address', 'timestamp'),
        Index('idx_security_severity', 'severity', 'timestamp'),
        Index('idx_security_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, type='{self.event_type}', severity='{self.severity}', blocked={self.blocked})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'details': self.details,
            'severity': self.severity,
            'blocked': self.blocked,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
