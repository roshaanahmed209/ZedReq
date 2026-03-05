"""Failed Login Attempt ORM Model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from config.database_orm import Base


class FailedLoginAttempt(Base):
    """SQLAlchemy ORM model for failed_login_attempts table"""
    __tablename__ = 'failed_login_attempts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(45), index=True)
    attempted_at = Column(DateTime, server_default=func.now(), index=True)
    success = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<FailedLoginAttempt(id={self.id}, username='{self.username}', success={self.success})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'ip_address': self.ip_address,
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at else None,
            'success': self.success,
        }
