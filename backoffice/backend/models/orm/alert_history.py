"""Alert History ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database_orm import Base


class AlertHistory(Base):
    """SQLAlchemy ORM model for alert_history table"""
    __tablename__ = 'alert_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey('alert_rules.id', ondelete='SET NULL'), index=True)
    triggered_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    metric_value = Column(Numeric(10, 2), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(String(50), nullable=False)
    sent = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime)
    
    # Relationships
    rule = relationship("AlertRule", foreign_keys=[rule_id])
    
    __table_args__ = (
        Index('idx_alerthistory_rule', 'rule_id', 'triggered_at'),
        Index('idx_alerthistory_triggered', 'triggered_at'),
        Index('idx_alerthistory_sent', 'sent', 'triggered_at'),
    )
    
    def __repr__(self):
        return f"<AlertHistory(id={self.id}, rule_id={self.rule_id}, sent={self.sent}, triggered_at={self.triggered_at})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'metric_value': float(self.metric_value) if self.metric_value else None,
            'message': self.message,
            'channel': self.channel,
            'sent': self.sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
        }
