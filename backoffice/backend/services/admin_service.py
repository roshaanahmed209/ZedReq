"""Admin service for backoffice operations"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from models.orm.admin_activity_log import AdminActivityLog
from models.orm.revenue_transaction import RevenueTransaction
from models.orm.cost_transaction import CostTransaction
from models.orm.financial_summary import FinancialSummary
import logging

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # User Management Methods
    # ========================================================================
    
    def get_all_users(
        self,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None,
        role: Optional[str] = None,
        subscription_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get paginated list of all users with filters
        
        Note: This is a placeholder for when we integrate with main ZedReq database.
        For now, returns empty list.
        """
        # TODO: When integrating with main database, query from users table
        # For now, return empty structure
        return {
            'users': [],
            'total': 0,
            'page': page,
            'limit': limit,
            'pages': 0
        }
    
    def get_user_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive user details
        
        Note: Placeholder for integration with main database
        """
        # TODO: Query from main users table when integrated
        return None
    
    def update_user_role(
        self,
        user_id: int,
        new_role: str,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Update user role (with audit log)
        
        Note: Placeholder for integration
        """
        # TODO: Implement when integrated with main database
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='user_role_update',
            target_type='user',
            target_id=user_id,
            details={'new_role': new_role},
            ip_address=ip_address,
            user_agent=user_agent
        )
        return True
    
    def suspend_user(
        self,
        user_id: int,
        reason: str,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Suspend a user account
        
        Note: Placeholder for integration
        """
        # TODO: Implement when integrated with main database
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='user_suspend',
            target_type='user',
            target_id=user_id,
            details={'reason': reason},
            ip_address=ip_address,
            user_agent=user_agent
        )
        return True
    
    # ========================================================================
    # Financial Analytics Methods
    # ========================================================================
    
    def get_revenue_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = 'day'  # 'day', 'week', 'month'
    ) -> Dict[str, Any]:
        """Get revenue analytics"""
        query = self.db.query(RevenueTransaction).filter(
            RevenueTransaction.status == 'completed'
        )
        
        if start_date:
            query = query.filter(RevenueTransaction.created_at >= start_date)
        if end_date:
            query = query.filter(RevenueTransaction.created_at <= end_date)
        
        # Group by period
        if group_by == 'day':
            period = func.date(RevenueTransaction.created_at)
        elif group_by == 'week':
            period = func.date_trunc('week', RevenueTransaction.created_at)
        elif group_by == 'month':
            period = func.date_trunc('month', RevenueTransaction.created_at)
        else:
            period = func.date(RevenueTransaction.created_at)
        
        revenue_data = query.with_entities(
            period.label('period'),
            func.sum(RevenueTransaction.amount).label('total'),
            func.count(RevenueTransaction.id).label('count')
        ).group_by(period).order_by(period).all()
        
        return {
            'revenue_by_period': [
                {
                    'period': str(r.period),
                    'total': float(r.total) if r.total else 0.0,
                    'count': r.count
                }
                for r in revenue_data
            ],
            'total_revenue': sum(float(r.total) if r.total else 0.0 for r in revenue_data),
            'total_transactions': sum(r.count for r in revenue_data)
        }
    
    def get_cost_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get cost analytics by category"""
        query = self.db.query(CostTransaction)
        
        if start_date:
            query = query.filter(CostTransaction.created_at >= start_date)
        if end_date:
            query = query.filter(CostTransaction.created_at <= end_date)
        
        costs_by_category = query.with_entities(
            CostTransaction.cost_category,
            func.sum(CostTransaction.amount).label('total'),
            func.count(CostTransaction.id).label('count')
        ).group_by(CostTransaction.cost_category).all()
        
        return {
            'costs_by_category': [
                {
                    'category': c.cost_category,
                    'total': float(c.total) if c.total else 0.0,
                    'count': c.count
                }
                for c in costs_by_category
            ],
            'total_costs': sum(float(c.total) if c.total else 0.0 for c in costs_by_category)
        }
    
    def get_cash_flow(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get cash flow analysis"""
        # Get revenue
        revenue_data = self.get_revenue_analytics(start_date, end_date, 'day')
        
        # Get costs
        cost_data = self.get_cost_analytics(start_date, end_date)
        
        # Calculate net cash flow
        total_revenue = revenue_data['total_revenue']
        total_costs = cost_data['total_costs']
        net_cash_flow = total_revenue - total_costs
        
        return {
            'revenue': revenue_data,
            'costs': cost_data,
            'net_cash_flow': net_cash_flow,
            'profit_margin': (net_cash_flow / total_revenue * 100) if total_revenue > 0 else 0.0
        }
    
    def get_subscription_metrics(self) -> Dict[str, Any]:
        """Get subscription metrics"""
        # Count active revenue transactions (subscriptions)
        active_subscriptions = self.db.query(RevenueTransaction).filter(
            and_(
                RevenueTransaction.transaction_type == 'subscription',
                RevenueTransaction.status == 'completed'
            )
        ).count()
        
        # Get plans breakdown
        plans_breakdown = self.db.query(
            RevenueTransaction.plan_type,
            func.count(RevenueTransaction.id).label('count')
        ).filter(
            and_(
                RevenueTransaction.transaction_type == 'subscription',
                RevenueTransaction.status == 'completed'
            )
        ).group_by(RevenueTransaction.plan_type).all()
        
        # Calculate MRR (Monthly Recurring Revenue)
        mrr = 0.0
        plan_prices = {'free': 0, 'pro': 29.99, 'premium': 99.99}  # Adjust as needed
        
        for plan, count in plans_breakdown:
            if plan and plan in plan_prices:
                mrr += plan_prices[plan] * count
        
        # Total users (placeholder - will be from main DB when integrated)
        total_users = active_subscriptions  # Placeholder
        
        return {
            'total_users': total_users,
            'active_subscriptions': active_subscriptions,
            'free_users': max(0, total_users - active_subscriptions),
            'plans_breakdown': {plan: count for plan, count in plans_breakdown if plan},
            'mrr': mrr,
            'conversion_rate': (active_subscriptions / total_users * 100) if total_users > 0 else 0.0
        }
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary with all key metrics"""
        # Get last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        revenue_data = self.get_revenue_analytics(start_date, end_date, 'day')
        cost_data = self.get_cost_analytics(start_date, end_date)
        cash_flow = self.get_cash_flow(start_date, end_date)
        subscription_metrics = self.get_subscription_metrics()
        
        # Recent transactions (last 10)
        recent_revenue = self.db.query(RevenueTransaction).filter(
            RevenueTransaction.status == 'completed'
        ).order_by(desc(RevenueTransaction.created_at)).limit(10).all()
        
        recent_costs = self.db.query(CostTransaction).order_by(
            desc(CostTransaction.created_at)
        ).limit(10).all()
        
        return {
            'revenue': {
                'total': revenue_data['total_revenue'],
                'transactions': revenue_data['total_transactions']
            },
            'costs': {
                'total': cost_data['total_costs'],
                'by_category': cost_data['costs_by_category']
            },
            'cash_flow': {
                'net': cash_flow['net_cash_flow'],
                'profit_margin': cash_flow['profit_margin']
            },
            'subscriptions': subscription_metrics,
            'recent_revenue': [r.to_dict() for r in recent_revenue],
            'recent_costs': [c.to_dict() for c in recent_costs]
        }
    
    # ========================================================================
    # Cost Tracking Helpers
    # ========================================================================
    
    def track_openai_cost(
        self,
        user_id: Optional[int],
        model: str,
        tokens_used: int,
        cost_per_1k_tokens: float,
        request_type: str = 'completion'
    ):
        """Track OpenAI API costs"""
        total_cost = (tokens_used / 1000) * cost_per_1k_tokens
        
        cost_transaction = CostTransaction(
            cost_category='openai',
            service_name=model,
            amount=total_cost,
            unit_type='token',
            quantity=tokens_used,
            user_id=user_id,
            extra_metadata={
                'model': model,
                'tokens_used': tokens_used,
                'cost_per_1k': cost_per_1k_tokens,
                'request_type': request_type
            }
        )
        
        self.db.add(cost_transaction)
        self.db.commit()
        logger.debug(f"Tracked OpenAI cost: ${total_cost:.4f} for {tokens_used} tokens")
    
    def track_tavus_cost(
        self,
        user_id: Optional[int],
        conversation_id: str,
        cost: float,
        duration_seconds: Optional[int] = None
    ):
        """Track Tavus API costs"""
        cost_transaction = CostTransaction(
            cost_category='tavus',
            service_name='tavus-api',
            amount=cost,
            unit_type='request',
            quantity=1,
            user_id=user_id,
            extra_metadata={
                'conversation_id': conversation_id,
                'duration_seconds': duration_seconds
            }
        )
        
        self.db.add(cost_transaction)
        self.db.commit()
        logger.debug(f"Tracked Tavus cost: ${cost:.4f}")
    
    # ========================================================================
    # Activity Logging
    # ========================================================================
    
    def _log_admin_activity(
        self,
        admin_id: int,
        action_type: str,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log admin activity for audit trail"""
        try:
            log_entry = AdminActivityLog(
                admin_id=admin_id,
                action_type=action_type,
                target_type=target_type,
                target_id=target_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging admin activity: {e}")
            self.db.rollback()
    
    def get_activity_logs(
        self,
        page: int = 1,
        limit: int = 50,
        admin_id: Optional[int] = None,
        action_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get paginated activity logs"""
        query = self.db.query(AdminActivityLog)
        
        if admin_id:
            query = query.filter(AdminActivityLog.admin_id == admin_id)
        if action_type:
            query = query.filter(AdminActivityLog.action_type == action_type)
        if start_date:
            query = query.filter(AdminActivityLog.created_at >= start_date)
        if end_date:
            query = query.filter(AdminActivityLog.created_at <= end_date)
        
        total = query.count()
        logs = query.order_by(desc(AdminActivityLog.created_at)).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        return {
            'logs': [log.to_dict() for log in logs],
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }
