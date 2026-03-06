"""Deployment Log ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class DeploymentLog(Base):
    """SQLAlchemy ORM model for deployment_logs table"""
    __tablename__ = 'deployment_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), nullable=False, index=True)
    deployment_type = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    status = Column(String(20), default='in_progress', index=True)
    success = Column(Boolean)
    rollback = Column(Boolean, default=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_deployment_version', 'version', 'start_time'),
        Index('idx_deployment_status', 'status', 'start_time'),
        Index('idx_deployment_start', 'start_time'),
    )
    
    def __repr__(self):
        return f"<DeploymentLog(id={self.id}, version='{self.version}', type='{self.deployment_type}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'version': self.version,
            'deployment_type': self.deployment_type,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'success': self.success,
            'rollback': self.rollback,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
