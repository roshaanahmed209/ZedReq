"""Financial service for revenue and cost tracking"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, date, timedelta
from models.orm.revenue_transaction import RevenueTransaction
from models.orm.cost_transaction import CostTransaction
from models.orm.financial_summary import FinancialSummary
import logging

logger = logging.getLogger(__name__)


class FinancialService:
    """Service for financial operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # Revenue Tracking
    # ========================================================================
    
    def create_revenue_transaction(
        self,
        transaction_type: str,
        amount: float,
        currency: str = 'USD',
        user_id: Optional[int] = None,
        plan_type: Optional[str] = None,
        provider: Optional[str] = None,
        provider_transaction_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        status: str = 'pending'
    ) -> RevenueTransaction:
        """Create a revenue transaction"""
        try:
            transaction = RevenueTransaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                currency=currency,
                plan_type=plan_type,
                provider=provider,
                provider_transaction_id=provider_transaction_id,
                status=status,
                description=description,
                extra_metadata=metadata or {}
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"Revenue transaction created: {transaction.id} - ${amount}")
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating revenue transaction: {e}", exc_info=True)
            raise
    
    def update_transaction_status(
        self,
        transaction_id: int,
        status: str,
        completed_at: Optional[datetime] = None
    ) -> bool:
        """Update transaction status"""
        try:
            transaction = self.db.query(RevenueTransaction).filter(
                RevenueTransaction.id == transaction_id
            ).first()
            
            if not transaction:
                return False
            
            transaction.status = status
            if completed_at:
                transaction.completed_at = completed_at
            elif status == 'completed':
                transaction.completed_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating transaction status: {e}")
            return False
    
    def get_transactions(
        self,
        page: int = 1,
        limit: int = 50,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get paginated list of transactions"""
        query = self.db.query(RevenueTransaction)
        
        if transaction_type:
            query = query.filter(RevenueTransaction.transaction_type == transaction_type)
        if status:
            query = query.filter(RevenueTransaction.status == status)
        if start_date:
            query = query.filter(RevenueTransaction.created_at >= start_date)
        if end_date:
            query = query.filter(RevenueTransaction.created_at <= end_date)
        
        total = query.count()
        transactions = query.order_by(desc(RevenueTransaction.created_at)).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        return {
            'transactions': [t.to_dict() for t in transactions],
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }
    
    # ========================================================================
    # Cost Tracking
    # ========================================================================
    
    def create_cost_transaction(
        self,
        cost_category: str,
        amount: float,
        service_name: Optional[str] = None,
        currency: str = 'USD',
        unit_type: Optional[str] = None,
        quantity: Optional[float] = None,
        user_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> CostTransaction:
        """Create a cost transaction"""
        try:
            transaction = CostTransaction(
                cost_category=cost_category,
                service_name=service_name,
                amount=amount,
                currency=currency,
                unit_type=unit_type,
                quantity=quantity,
                user_id=user_id,
                extra_metadata=metadata or {}
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"Cost transaction created: {transaction.id} - ${amount} ({cost_category})")
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating cost transaction: {e}", exc_info=True)
            raise
    
    def get_cost_transactions(
        self,
        page: int = 1,
        limit: int = 50,
        cost_category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get paginated list of cost transactions"""
        query = self.db.query(CostTransaction)
        
        if cost_category:
            query = query.filter(CostTransaction.cost_category == cost_category)
        if start_date:
            query = query.filter(CostTransaction.created_at >= start_date)
        if end_date:
            query = query.filter(CostTransaction.created_at <= end_date)
        
        total = query.count()
        transactions = query.order_by(desc(CostTransaction.created_at)).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        return {
            'transactions': [t.to_dict() for t in transactions],
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }
    
    # ========================================================================
    # Financial Summary Generation
    # ========================================================================
    
    def generate_financial_summary(
        self,
        period_type: str,
        period_start: date,
        period_end: date
    ) -> FinancialSummary:
        """Generate financial summary for a period"""
        try:
            # Check if summary already exists
            existing = self.db.query(FinancialSummary).filter(
                and_(
                    FinancialSummary.period_type == period_type,
                    FinancialSummary.period_start == period_start
                )
            ).first()
            
            if existing:
                # Update existing summary
                summary = existing
            else:
                summary = FinancialSummary(
                    period_type=period_type,
                    period_start=period_start,
                    period_end=period_end
                )
                self.db.add(summary)
            
            # Calculate revenue
            revenue_query = self.db.query(RevenueTransaction).filter(
                and_(
                    RevenueTransaction.status == 'completed',
                    RevenueTransaction.created_at >= datetime.combine(period_start, datetime.min.time()),
                    RevenueTransaction.created_at <= datetime.combine(period_end, datetime.max.time())
                )
            )
            
            total_revenue = revenue_query.with_entities(
                func.sum(RevenueTransaction.amount)
            ).scalar() or 0.0
            
            subscription_revenue = revenue_query.filter(
                RevenueTransaction.transaction_type == 'subscription'
            ).with_entities(func.sum(RevenueTransaction.amount)).scalar() or 0.0
            
            one_time_revenue = revenue_query.filter(
                RevenueTransaction.transaction_type == 'one_time'
            ).with_entities(func.sum(RevenueTransaction.amount)).scalar() or 0.0
            
            refunds = revenue_query.filter(
                RevenueTransaction.transaction_type == 'refund'
            ).with_entities(func.sum(RevenueTransaction.amount)).scalar() or 0.0
            
            # Calculate costs
            cost_query = self.db.query(CostTransaction).filter(
                and_(
                    CostTransaction.created_at >= datetime.combine(period_start, datetime.min.time()),
                    CostTransaction.created_at <= datetime.combine(period_end, datetime.max.time())
                )
            )
            
            total_costs = cost_query.with_entities(
                func.sum(CostTransaction.amount)
            ).scalar() or 0.0
            
            openai_costs = cost_query.filter(
                CostTransaction.cost_category == 'openai'
            ).with_entities(func.sum(CostTransaction.amount)).scalar() or 0.0
            
            tavus_costs = cost_query.filter(
                CostTransaction.cost_category == 'tavus'
            ).with_entities(func.sum(CostTransaction.amount)).scalar() or 0.0
            
            infrastructure_costs = cost_query.filter(
                CostTransaction.cost_category == 'infrastructure'
            ).with_entities(func.sum(CostTransaction.amount)).scalar() or 0.0
            
            storage_costs = cost_query.filter(
                CostTransaction.cost_category == 'storage'
            ).with_entities(func.sum(CostTransaction.amount)).scalar() or 0.0
            
            other_costs = cost_query.filter(
                ~CostTransaction.cost_category.in_(['openai', 'tavus', 'infrastructure', 'storage'])
            ).with_entities(func.sum(CostTransaction.amount)).scalar() or 0.0
            
            # Subscription metrics
            active_subscriptions = revenue_query.filter(
                RevenueTransaction.transaction_type == 'subscription'
            ).count()
            
            # Calculate profit
            net_profit = float(total_revenue) - float(total_costs)
            profit_margin = (net_profit / float(total_revenue) * 100) if total_revenue > 0 else 0.0
            
            # Update summary
            summary.total_revenue = total_revenue
            summary.subscription_revenue = subscription_revenue
            summary.one_time_revenue = one_time_revenue
            summary.refunds = refunds
            summary.total_costs = total_costs
            summary.openai_costs = openai_costs
            summary.tavus_costs = tavus_costs
            summary.infrastructure_costs = infrastructure_costs
            summary.storage_costs = storage_costs
            summary.other_costs = other_costs
            summary.active_subscriptions = active_subscriptions
            summary.net_profit = net_profit
            summary.profit_margin = profit_margin
            
            self.db.commit()
            self.db.refresh(summary)
            
            logger.info(f"Financial summary generated: {period_type} - {period_start}")
            return summary
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating financial summary: {e}", exc_info=True)
            raise
    
    def get_financial_summaries(
        self,
        period_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get financial summaries"""
        query = self.db.query(FinancialSummary)
        
        if period_type:
            query = query.filter(FinancialSummary.period_type == period_type)
        if start_date:
            query = query.filter(FinancialSummary.period_start >= start_date)
        if end_date:
            query = query.filter(FinancialSummary.period_start <= end_date)
        
        summaries = query.order_by(desc(FinancialSummary.period_start)).limit(limit).all()
        
        return [s.to_dict() for s in summaries]
