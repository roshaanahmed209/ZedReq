"""Admin Activity Log ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database_orm import Base


class AdminActivityLog(Base):
    """SQLAlchemy ORM model for admin_activity_log table"""
    __tablename__ = 'admin_activity_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    action_type = Column(String(50), nullable=False, index=True)
    target_type = Column(String(50), index=True)
    target_id = Column(Integer, index=True)
    details = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    admin = relationship("AdminUser", back_populates="activity_logs")
    
    def __repr__(self):
        return f"<AdminActivityLog(id={self.id}, admin_id={self.admin_id}, action='{self.action_type}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action_type': self.action_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
