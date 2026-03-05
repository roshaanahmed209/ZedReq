"""Financial Summary ORM Model"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, UniqueConstraint
from sqlalchemy.sql import func

from config.database_orm import Base


class FinancialSummary(Base):
    """SQLAlchemy ORM model for financial_summaries table"""
    __tablename__ = 'financial_summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    period_type = Column(String(20), nullable=False, index=True)
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False)
    
    # Revenue
    total_revenue = Column(Numeric(12, 2), default=0)
    subscription_revenue = Column(Numeric(12, 2), default=0)
    one_time_revenue = Column(Numeric(12, 2), default=0)
    refunds = Column(Numeric(12, 2), default=0)
    
    # Costs
    total_costs = Column(Numeric(12, 4), default=0)
    openai_costs = Column(Numeric(12, 4), default=0)
    tavus_costs = Column(Numeric(12, 4), default=0)
    infrastructure_costs = Column(Numeric(12, 4), default=0)
    storage_costs = Column(Numeric(12, 4), default=0)
    other_costs = Column(Numeric(12, 4), default=0)
    
    # Metrics
    active_subscriptions = Column(Integer, default=0)
    new_subscriptions = Column(Integer, default=0)
    cancelled_subscriptions = Column(Integer, default=0)
    churn_rate = Column(Numeric(5, 2), default=0)
    
    # Profit
    net_profit = Column(Numeric(12, 2), default=0)
    profit_margin = Column(Numeric(5, 2), default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('period_type', 'period_start', name='uq_financial_summary_period'),
    )
    
    def __repr__(self):
        return f"<FinancialSummary(id={self.id}, period='{self.period_type}', start={self.period_start})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'period_type': self.period_type,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'total_revenue': float(self.total_revenue) if self.total_revenue else 0.0,
            'subscription_revenue': float(self.subscription_revenue) if self.subscription_revenue else 0.0,
            'one_time_revenue': float(self.one_time_revenue) if self.one_time_revenue else 0.0,
            'refunds': float(self.refunds) if self.refunds else 0.0,
            'total_costs': float(self.total_costs) if self.total_costs else 0.0,
            'openai_costs': float(self.openai_costs) if self.openai_costs else 0.0,
            'tavus_costs': float(self.tavus_costs) if self.tavus_costs else 0.0,
            'infrastructure_costs': float(self.infrastructure_costs) if self.infrastructure_costs else 0.0,
            'storage_costs': float(self.storage_costs) if self.storage_costs else 0.0,
            'other_costs': float(self.other_costs) if self.other_costs else 0.0,
            'active_subscriptions': self.active_subscriptions,
            'new_subscriptions': self.new_subscriptions,
            'cancelled_subscriptions': self.cancelled_subscriptions,
            'churn_rate': float(self.churn_rate) if self.churn_rate else 0.0,
            'net_profit': float(self.net_profit) if self.net_profit else 0.0,
            'profit_margin': float(self.profit_margin) if self.profit_margin else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
