"""Infrastructure Metric ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class InfrastructureMetric(Base):
    """SQLAlchemy ORM model for infrastructure_metrics table"""
    __tablename__ = 'infrastructure_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    cpu_percent = Column(Numeric(5, 2), nullable=False)
    ram_percent = Column(Numeric(5, 2), nullable=False)
    ram_used_mb = Column(Numeric(10, 2), nullable=False)
    ram_total_mb = Column(Numeric(10, 2), nullable=False)
    disk_percent = Column(Numeric(5, 2), nullable=False)
    disk_used_gb = Column(Numeric(10, 2), nullable=False)
    disk_total_gb = Column(Numeric(10, 2), nullable=False)
    network_in_mb = Column(Numeric(10, 2), default=0)
    network_out_mb = Column(Numeric(10, 2), default=0)
    server_name = Column(String(100), default='main', index=True)
    
    __table_args__ = (
        Index('idx_infrastructure_timestamp', 'timestamp'),
        Index('idx_infrastructure_server', 'server_name', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<InfrastructureMetric(id={self.id}, server='{self.server_name}', cpu={self.cpu_percent}%, timestamp={self.timestamp})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'cpu_percent': float(self.cpu_percent) if self.cpu_percent else None,
            'ram_percent': float(self.ram_percent) if self.ram_percent else None,
            'ram_used_mb': float(self.ram_used_mb) if self.ram_used_mb else None,
            'ram_total_mb': float(self.ram_total_mb) if self.ram_total_mb else None,
            'disk_percent': float(self.disk_percent) if self.disk_percent else None,
            'disk_used_gb': float(self.disk_used_gb) if self.disk_used_gb else None,
            'disk_total_gb': float(self.disk_total_gb) if self.disk_total_gb else None,
            'network_in_mb': float(self.network_in_mb) if self.network_in_mb else None,
            'network_out_mb': float(self.network_out_mb) if self.network_out_mb else None,
            'server_name': self.server_name,
        }
