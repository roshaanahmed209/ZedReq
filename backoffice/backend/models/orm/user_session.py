"""User Session ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class UserSession(Base):
    """SQLAlchemy ORM model for user_sessions table"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    start_time = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    last_activity = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    page_views = Column(Integer, default=0)
    device_type = Column(String(50))
    browser = Column(String(100))
    os = Column(String(100))
    country = Column(String(100))
    ip_address = Column(String(45))
    
    __table_args__ = (
        Index('idx_sessions_user', 'user_id', 'start_time'),
        Index('idx_sessions_session', 'session_id'),
        Index('idx_sessions_start', 'start_time'),
        Index('idx_sessions_active', 'last_activity'),
    )
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, session_id='{self.session_id}', active={self.end_time is None})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'page_views': self.page_views,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'country': self.country,
            'ip_address': self.ip_address,
        }
