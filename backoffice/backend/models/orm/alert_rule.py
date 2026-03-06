"""Alert Rule ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, ARRAY
from sqlalchemy.sql import func

from config.database_orm import Base


class AlertRule(Base):
    """SQLAlchemy ORM model for alert_rules table"""
    __tablename__ = 'alert_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(100), unique=True, nullable=False)
    metric_type = Column(String(50), nullable=False, index=True)
    threshold = Column(Numeric(10, 2), nullable=False)
    condition = Column(String(20), nullable=False)  # 'greater_than', 'less_than', 'equals'
    enabled = Column(Boolean, default=True, index=True)
    channels = Column(ARRAY(String), default=['email'])
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.rule_name}', type='{self.metric_type}', enabled={self.enabled})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'metric_type': self.metric_type,
            'threshold': float(self.threshold) if self.threshold else None,
            'condition': self.condition,
            'enabled': self.enabled,
            'channels': self.channels or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
