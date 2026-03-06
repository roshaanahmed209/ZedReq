"""Uptime Incident ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ARRAY, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class UptimeIncident(Base):
    """SQLAlchemy ORM model for uptime_incidents table"""
    __tablename__ = 'uptime_incidents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_type = Column(String(50), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    status = Column(String(20), default='active', index=True)
    description = Column(Text)
    affected_services = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_uptime_start', 'start_time'),
        Index('idx_uptime_status', 'status'),
        Index('idx_uptime_type', 'incident_type'),
    )
    
    def __repr__(self):
        return f"<UptimeIncident(id={self.id}, type='{self.incident_type}', status='{self.status}', start={self.start_time})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'incident_type': self.incident_type,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'status': self.status,
            'description': self.description,
            'affected_services': self.affected_services or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
