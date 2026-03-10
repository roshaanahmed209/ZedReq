"""Financial Tracking Service for backoffice"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, date
from models.orm.user_payment_summary import UserPaymentSummary
from models.orm.bearable_cost import BearableCost
from config.database_orm import get_main_app_engine
import logging

logger = logging.getLogger(__name__)


class FinancialTrackingService:
    """Service for financial tracking and profit calculations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def sync_user_payment_summary(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Sync payment data from main app payment table to user_payment_summary.
        If user_id is provided, syncs single user. If None, syncs all users.
        """
        try:
            engine = get_main_app_engine()
            synced_count = 0
            
            with engine.connect() as conn:
                if user_id:
                    # Sync single user
                    user_ids = [user_id]
                else:
                    # Get all users with payments
                    users_query = text("""
                        SELECT DISTINCT uid 
                        FROM payment 
                        WHERE uid IS NOT NULL
                    """)
                    user_results = conn.execute(users_query).fetchall()
                    user_ids = [row[0] for row in user_results]
                
                for uid in user_ids:
                    # Get payment summary for this user
                    payment_query = text("""
                        SELECT 
                            COALESCE(SUM(CASE WHEN amount IS NOT NULL AND amount > 0 THEN amount ELSE 0 END), 0) as total_paid,
                            COALESCE(SUM(CASE WHEN amount IS NOT NULL AND amount < 0 THEN ABS(amount) ELSE 0 END), 0) as total_refunded,
                            MAX(payment_date) as last_payment_date,
                            (SELECT amount FROM payment 
                             WHERE uid = :uid AND payment_date = (SELECT MAX(payment_date) FROM payment WHERE uid = :uid AND amount > 0)
                             LIMIT 1) as last_paid_amount,
                            (SELECT subscription_plan FROM payment WHERE uid = :uid ORDER BY payment_date DESC LIMIT 1) as current_plan
                        FROM payment
                        WHERE uid = :uid
                    """)
                    
                    result = conn.execute(payment_query, {'uid': uid}).fetchone()
                    
                    if result:
                        total_paid = float(result[0] or 0.0)
                        total_refunded = float(result[1] or 0.0)
                        last_payment_date = result[2]
                        last_paid_amount = float(result[3] or 0.0) if result[3] else None
                        current_plan = result[4]
                        
                        # Get plan_id from subscription_plans if plan name exists
                        plan_id = None
                        if current_plan:
                            plan_query = text("""
                                SELECT plan_id FROM subscription_plans 
                                WHERE plan_name = :plan_name AND is_active = TRUE
                                LIMIT 1
                            """)
                            plan_result = conn.execute(plan_query, {'plan_name': current_plan}).fetchone()
                            if plan_result:
                                plan_id = plan_result[0]
                        
                        # Upsert user payment summary
                        summary = self.db.query(UserPaymentSummary).filter(
                            UserPaymentSummary.user_id == uid
                        ).first()
                        
                        if summary:
                            summary.total_amount_paid = total_paid
                            summary.total_refunded = total_refunded
                            summary.last_paid_amount = last_paid_amount
                            summary.last_payment_date = last_payment_date
                            summary.plan_id = plan_id
                        else:
                            summary = UserPaymentSummary(
                                user_id=uid,
                                plan_id=plan_id,
                                total_amount_paid=total_paid,
                                total_refunded=total_refunded,
                                last_paid_amount=last_paid_amount,
                                last_payment_date=last_payment_date
                            )
                            self.db.add(summary)
                        
                        synced_count += 1
            
            self.db.commit()
            logger.info(f"Synced payment summaries for {synced_count} user(s)")
            return {'synced_count': synced_count, 'success': True}
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error syncing user payment summary: {e}", exc_info=True)
            raise
    
    def calculate_tavus_costs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate Tavus costs based on usage_tracking table.
        Gets total interview sessions and multiplies by cost per session.
        """
        try:
            # Get Tavus cost per session from bearable_costs
            tavus_cost = self.db.query(BearableCost).filter(
                BearableCost.cost_name == "Tavus Session"
            ).first()
            
            if not tavus_cost:
                logger.warning("Tavus Session cost not found in bearable_costs. Using default $0.25")
                cost_per_session = 0.25
            else:
                cost_per_session = float(tavus_cost.amount)
            
            # Query usage_tracking from main app
            engine = get_main_app_engine()
            with engine.connect() as conn:
                # Build date filter
                date_filter = ""
                params = {}
                
                if start_date:
                    date_filter += " AND period_start >= :start_date"
                    params['start_date'] = start_date.date() if isinstance(start_date, datetime) else start_date
                
                if end_date:
                    date_filter += " AND period_start <= :end_date"
                    params['end_date'] = end_date.date() if isinstance(end_date, datetime) else end_date
                
                if user_id:
                    date_filter += " AND user_id = :user_id"
                    params['user_id'] = user_id
                
                # Query usage_tracking for interview_sessions
                usage_query = text(f"""
                    SELECT 
                        COALESCE(SUM(usage_count), 0) as total_sessions
                    FROM usage_tracking
                    WHERE feature = 'interview_sessions'
                    {date_filter}
                """)
                
                result = conn.execute(usage_query, params).fetchone()
                total_sessions = int(result[0] or 0) if result else 0
                
                total_cost = total_sessions * cost_per_session
                
                return {
                    'total_sessions': total_sessions,
                    'cost_per_session': cost_per_session,
                    'total_cost': total_cost
                }
                
        except Exception as e:
            logger.error(f"Error calculating Tavus costs: {e}", exc_info=True)
            return {
                'total_sessions': 0,
                'cost_per_session': 0.25,
                'total_cost': 0.0
            }
    
    def calculate_fixed_costs(self) -> Dict[str, Any]:
        """Calculate fixed costs from bearable_costs table"""
        try:
            fixed_costs = self.db.query(BearableCost).filter(
                BearableCost.is_fixed == True
            ).all()
            
            costs_list = []
            total = 0.0
            
            for cost in fixed_costs:
                amount = float(cost.amount)
                costs_list.append({
                    'id': cost.id,
                    'cost_name': cost.cost_name,
                    'amount': amount,
                    'unit_type': cost.unit_type
                })
                total += amount
            
            return {
                'costs': costs_list,
                'total': total
            }
            
        except Exception as e:
            logger.error(f"Error calculating fixed costs: {e}", exc_info=True)
            return {'costs': [], 'total': 0.0}
    
    def calculate_net_profit(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate net profit:
        - Total revenue from main app payment table (real-time, accurate)
        - Minus refunds (negative amounts from payment table)
        - Minus Tavus costs (calculated from usage_tracking)
        - Minus fixed costs
        """
        try:
            # Get revenue and refunds directly from main app payment table for accuracy
            engine = get_main_app_engine()
            with engine.connect() as conn:
                # Build date filter
                date_filter = ""
                params = {}
                
                if start_date:
                    date_filter += " AND payment_date >= :start_date"
                    params['start_date'] = start_date
                if end_date:
                    date_filter += " AND payment_date <= :end_date"
                    params['end_date'] = end_date
                
                # Query payment table for revenue (positive amounts) and refunds (negative amounts)
                revenue_query = text(f"""
                    SELECT 
                        COALESCE(SUM(CASE WHEN amount IS NOT NULL AND amount > 0 THEN amount ELSE 0 END), 0) as total_revenue,
                        COALESCE(SUM(CASE WHEN amount IS NOT NULL AND amount < 0 THEN ABS(amount) ELSE 0 END), 0) as total_refunded
                    FROM payment
                    WHERE amount IS NOT NULL
                    {date_filter}
                """)
                
                result = conn.execute(revenue_query, params).fetchone()
                
                total_revenue = float(result[0] or 0.0) if result else 0.0
                total_refunded = float(result[1] or 0.0) if result else 0.0
                net_revenue = total_revenue - total_refunded
            
            # Calculate Tavus costs
            tavus_costs_data = self.calculate_tavus_costs(start_date, end_date)
            tavus_total_cost = tavus_costs_data['total_cost']
            
            # Calculate fixed costs
            fixed_costs_data = self.calculate_fixed_costs()
            fixed_total_cost = fixed_costs_data['total']
            
            # Total costs
            total_costs = tavus_total_cost + fixed_total_cost
            
            # Net profit
            net_profit = net_revenue - total_costs
            
            # Profit margin
            profit_margin = (net_profit / net_revenue * 100) if net_revenue > 0 else 0.0
            
            return {
                'total_revenue': total_revenue,
                'total_refunded': total_refunded,
                'net_revenue': net_revenue,
                'tavus_costs': tavus_costs_data,
                'fixed_costs': fixed_costs_data,
                'total_costs': total_costs,
                'net_profit': net_profit,
                'profit_margin': profit_margin
            }
            
        except Exception as e:
            logger.error(f"Error calculating net profit: {e}", exc_info=True)
            raise
    
    def get_user_financial_summary(self, user_id: int) -> Dict[str, Any]:
        """Get user-specific financial summary"""
        try:
            # Get user payment summary
            summary = self.db.query(UserPaymentSummary).filter(
                UserPaymentSummary.user_id == user_id
            ).first()
            
            if not summary:
                # Try to sync first
                self.sync_user_payment_summary(user_id)
                summary = self.db.query(UserPaymentSummary).filter(
                    UserPaymentSummary.user_id == user_id
                ).first()
            
            if not summary:
                return {
                    'user_id': user_id,
                    'total_amount_paid': 0.0,
                    'total_refunded': 0.0,
                    'net_revenue': 0.0,
                    'tavus_sessions': 0,
                    'tavus_cost': 0.0,
                    'total_cost': 0.0,
                    'net_profit': 0.0
                }
            
            # Calculate user-specific Tavus costs
            tavus_data = self.calculate_tavus_costs(user_id=user_id)
            
            # User doesn't pay fixed costs directly, but we can show their share
            # For now, we'll just show their variable costs (Tavus)
            user_total_cost = tavus_data['total_cost']
            user_net_profit = float(summary.total_amount_paid) - float(summary.total_refunded) - user_total_cost
            
            return {
                'user_id': user_id,
                'plan_id': summary.plan_id,
                'total_amount_paid': float(summary.total_amount_paid),
                'total_refunded': float(summary.total_refunded),
                'net_revenue': float(summary.total_amount_paid) - float(summary.total_refunded),
                'last_paid_amount': float(summary.last_paid_amount) if summary.last_paid_amount else None,
                'last_payment_date': summary.last_payment_date.isoformat() + 'Z' if summary.last_payment_date else None,
                'tavus_sessions': tavus_data['total_sessions'],
                'tavus_cost': tavus_data['total_cost'],
                'total_cost': user_total_cost,
                'net_profit': user_net_profit
            }
            
        except Exception as e:
            logger.error(f"Error getting user financial summary: {e}", exc_info=True)
            raise
    
    def refresh_all_summaries(self) -> Dict[str, Any]:
        """Sync all users from main app"""
        return self.sync_user_payment_summary(user_id=None)
