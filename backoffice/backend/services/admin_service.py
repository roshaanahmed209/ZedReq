"""Admin service for backoffice operations"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text
from datetime import datetime, timedelta
from models.orm.admin_activity_log import AdminActivityLog
from models.orm.revenue_transaction import RevenueTransaction
from models.orm.cost_transaction import CostTransaction
from models.orm.financial_summary import FinancialSummary
from config.database_orm import get_main_app_engine
from config.settings import settings
import secrets
import hashlib
import logging
import json

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
        Get paginated list of all users with filters from main app database
        """
        try:
            engine = get_main_app_engine()
            with engine.connect() as conn:
                # Build WHERE clause
                where_conditions = []
                params = {}
                
                if search:
                    where_conditions.append(
                        "(username ILIKE :search OR user_email ILIKE :search OR name ILIKE :search)"
                    )
                    params['search'] = f'%{search}%'
                
                if role:
                    where_conditions.append("role = :role")
                    params['role'] = role
                
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                
                # Get total count
                count_query = text(f"""
                    SELECT COUNT(*) 
                    FROM users 
                    WHERE {where_clause}
                """)
                total = conn.execute(count_query, params).scalar() or 0
                
                # Get paginated users
                offset = (page - 1) * limit
                users_query = text(f"""
                    SELECT 
                        u.uid,
                        u.username,
                        u.user_email,
                        u.name,
                        u.created_at,
                        u.updated_at,
                        u.last_login,
                        p.subscription_status,
                        p.subscription_plan,
                        p.trial_taken
                    FROM users u
                    LEFT JOIN payment p ON u.uid = p.uid
                    WHERE {where_clause}
                    ORDER BY u.created_at DESC
                    LIMIT :limit OFFSET :offset
                """)
                params['limit'] = limit
                params['offset'] = offset
                
                # Handle subscription_status filter
                if subscription_status:
                    if subscription_status == 'active':
                        where_clause += " AND p.subscription_status = 'active'"
                    elif subscription_status == 'inactive':
                        where_clause += " AND (p.subscription_status = 'inactive' OR p.subscription_status IS NULL)"
                    # Re-execute with updated where clause
                    users_query = text(f"""
                        SELECT 
                            u.uid,
                            u.username,
                            u.user_email,
                            u.name,
                            u.created_at,
                            u.updated_at,
                            u.last_login,
                            p.subscription_status,
                            p.subscription_plan,
                            p.trial_taken
                        FROM users u
                        LEFT JOIN payment p ON u.uid = p.uid
                        WHERE {where_clause}
                        ORDER BY u.created_at DESC
                        LIMIT :limit OFFSET :offset
                    """)
                
                users_result = conn.execute(users_query, params).fetchall()
                
                users = []
                for row in users_result:
                    user_dict = {
                        'id': row.uid,
                        'username': row.username,
                        'email': row.user_email,
                        'full_name': row.name,
                        'subscription_status': row.subscription_status or 'inactive',
                        'subscription_plan': row.subscription_plan or 'free',
                        'trial_taken': row.trial_taken or False,
                        'last_login': row.last_login.isoformat() + 'Z' if row.last_login else None,
                        'created_at': row.created_at.isoformat() + 'Z' if row.created_at else None,
                        'updated_at': row.updated_at.isoformat() + 'Z' if row.updated_at else None,
                    }
                    users.append(user_dict)
                
                pages = (total + limit - 1) // limit if total > 0 else 0
                
                return {
                    'users': users,
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'pages': pages
                }
        except Exception as e:
            error_msg = f"Error querying main app database for users: {e}"
            logger.error(error_msg, exc_info=True)
            # Re-raise with more context for API to handle
            raise Exception(f"Database connection error: {str(e)}. Please check MAIN_APP_DB_* environment variables in backoffice/.env file.")
    
    def get_user_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive user details from main app database
        """
        try:
            engine = get_main_app_engine()
            with engine.connect() as conn:
                # Get user details with payment info
                user_query = text("""
                    SELECT 
                        u.uid,
                        u.username,
                        u.user_email,
                        u.name,
                        u.created_at,
                        u.updated_at,
                        u.last_login,
                        u.profile_url,
                        p.subscription_status,
                        p.subscription_plan,
                        p.subscription_start,
                        p.subscription_end,
                        p.trial_taken,
                        p.trial_end,
                        p.payment_provider,
                        p.billing_email
                    FROM users u
                    LEFT JOIN payment p ON u.uid = p.uid
                    WHERE u.uid = :user_id
                """)
                user_result = conn.execute(user_query, {'user_id': user_id}).fetchone()
                
                if not user_result:
                    return None
                
                # Get user stats (connections, posts, etc.)
                stats_query = text("""
                    SELECT 
                        (SELECT COUNT(*) FROM connections WHERE follower_uid = :user_id OR followed_uid = :user_id) as connections_count,
                        (SELECT COUNT(*) FROM post WHERE uid = :user_id AND is_deleted = FALSE) as posts_count
                """)
                stats_result = conn.execute(stats_query, {'user_id': user_id}).fetchone()
                
                user_dict = {
                    'id': user_result.uid,
                    'username': user_result.username,
                    'email': user_result.user_email,
                    'full_name': user_result.name,
                    'profile_url': user_result.profile_url,
                    'subscription': {
                        'status': user_result.subscription_status or 'inactive',
                        'plan': user_result.subscription_plan or 'free',
                        'start': user_result.subscription_start.isoformat() + 'Z' if user_result.subscription_start else None,
                        'end': user_result.subscription_end.isoformat() + 'Z' if user_result.subscription_end else None,
                        'trial_taken': user_result.trial_taken or False,
                        'trial_end': user_result.trial_end.isoformat() + 'Z' if user_result.trial_end else None,
                        'payment_provider': user_result.payment_provider,
                        'billing_email': user_result.billing_email,
                    },
                    'stats': {
                        'connections': stats_result.connections_count or 0 if stats_result else 0,
                        'posts': stats_result.posts_count or 0 if stats_result else 0,
                    },
                    'last_login': user_result.last_login.isoformat() + 'Z' if user_result.last_login else None,
                    'created_at': user_result.created_at.isoformat() + 'Z' if user_result.created_at else None,
                    'updated_at': user_result.updated_at.isoformat() + 'Z' if user_result.updated_at else None,
                }
                
                return user_dict
        except Exception as e:
            logger.error(f"Error getting user details: {e}", exc_info=True)
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
    
    def change_user_plan(
        self,
        user_id: int,
        new_plan: str,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Change a user's subscription plan (payment-first flow).
        
        Write order (payment is source of truth):
        1. Verify user exists + look up plan_id.
        2. UPSERT payment table FIRST (plan, status).
        3. UPSERT user_subscriptions (synced from payment, used for quota reads).
        4. SET payment.subscription_id FK link.
        
        All writes happen inside a single engine.begin() transaction.
        """
        valid_plans = ('free', 'pro', 'premium', 'enterprise')
        if new_plan not in valid_plans:
            raise ValueError(f"Invalid plan. Must be one of: {', '.join(valid_plans)}")
        
        engine = get_main_app_engine()
        new_status = 'active' if new_plan != 'free' else 'inactive'
        
        with engine.begin() as conn:
            # 1. Verify user exists
            user_check = conn.execute(
                text("SELECT uid FROM users WHERE uid = :uid"),
                {'uid': user_id}
            ).fetchone()
            if not user_check:
                raise ValueError("User not found")
            
            # 2. Look up plan_id from subscription_plans
            plan_row = conn.execute(
                text("SELECT plan_id FROM subscription_plans WHERE plan_name = :plan AND is_active = TRUE"),
                {'plan': new_plan}
            ).fetchone()
            if not plan_row:
                raise ValueError(f"Plan '{new_plan}' not found in subscription_plans. Ensure plans are seeded.")
            plan_id = plan_row[0]
            
            # 3. UPSERT payment FIRST (source of truth)
            pay_result = conn.execute(
                text("""
                    UPDATE payment
                    SET subscription_plan = :plan, subscription_status = :status, updated_at = NOW()
                    WHERE uid = :uid
                """),
                {'plan': new_plan, 'status': new_status, 'uid': user_id}
            )
            
            if pay_result.rowcount == 0:
                # No payment row exists; create one
                conn.execute(
                    text("""
                        INSERT INTO payment (uid, subscription_plan, subscription_status,
                                             payment_provider, created_at, updated_at)
                        VALUES (:uid, :plan, :status, 'admin_override', NOW(), NOW())
                    """),
                    {'uid': user_id, 'plan': new_plan, 'status': new_status}
                )
            
            # 4. UPSERT user_subscriptions (synced from payment, used for quota reads)
            existing_sub = conn.execute(
                text("SELECT subscription_id FROM user_subscriptions WHERE user_id = :uid"),
                {'uid': user_id}
            ).fetchone()
            
            if existing_sub:
                conn.execute(
                    text("""
                        UPDATE user_subscriptions
                        SET plan_id = :plan_id, status = :status, assigned_by = 'admin',
                            started_at = NOW(), updated_at = NOW()
                        WHERE user_id = :uid
                    """),
                    {'plan_id': plan_id, 'status': new_status, 'uid': user_id}
                )
                subscription_id = existing_sub[0]
            else:
                result = conn.execute(
                    text("""
                        INSERT INTO user_subscriptions (user_id, plan_id, status, assigned_by, started_at, created_at, updated_at)
                        VALUES (:uid, :plan_id, :status, 'admin', NOW(), NOW(), NOW())
                        RETURNING subscription_id
                    """),
                    {'uid': user_id, 'plan_id': plan_id, 'status': new_status}
                )
                subscription_id = result.fetchone()[0]
            
            # 5. SET payment.subscription_id FK link
            conn.execute(
                text("UPDATE payment SET subscription_id = :sub_id WHERE uid = :uid"),
                {'sub_id': subscription_id, 'uid': user_id}
            )
        
        # Audit log (backoffice DB only)
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='change_user_plan',
            target_type='user',
            target_id=user_id,
            details={'new_plan': new_plan, 'new_status': new_status, 'subscription_id': subscription_id},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {'success': True, 'message': f'Plan changed to {new_plan}', 'plan': new_plan, 'status': new_status}
    
    def cancel_subscription(
        self,
        user_id: int,
        reason: str,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel a user's subscription (payment-first).
        Payment is updated first (source of truth), then user_subscriptions is synced.
        """
        engine = get_main_app_engine()
        with engine.begin() as conn:
            # 1. Cancel in payment FIRST (source of truth)
            pay_result = conn.execute(
                text("""
                    UPDATE payment 
                    SET subscription_status = 'cancelled', updated_at = NOW()
                    WHERE uid = :uid AND subscription_status = 'active'
                """),
                {'uid': user_id}
            )
            
            # 2. Cancel in user_subscriptions (synced from payment)
            sub_result = conn.execute(
                text("""
                    UPDATE user_subscriptions
                    SET status = 'cancelled', updated_at = NOW()
                    WHERE user_id = :uid AND status = 'active'
                """),
                {'uid': user_id}
            )
            
            if pay_result.rowcount == 0 and sub_result.rowcount == 0:
                raise ValueError("No active subscription found for this user")
        
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='cancel_subscription',
            target_type='user',
            target_id=user_id,
            details={'reason': reason[:500]},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {'success': True, 'message': 'Subscription cancelled'}
    
    def unsuspend_user(
        self,
        user_id: int,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unsuspend a user account.
        Log-only in backoffice DB — zero writes to main app DB.
        """
        # Verify user exists (read-only)
        engine = get_main_app_engine()
        with engine.connect() as conn:
            user_check = conn.execute(
                text("SELECT uid FROM users WHERE uid = :uid"),
                {'uid': user_id}
            ).fetchone()
            if not user_check:
                raise ValueError("User not found")
        
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='unsuspend_user',
            target_type='user',
            target_id=user_id,
            details={'action': 'unsuspend'},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {'success': True, 'message': 'User unsuspended'}
    
    def reset_user_password(
        self,
        user_id: int,
        new_password: str,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reset a user's password to the admin-provided value.
        Single UPDATE on users table: password_hash.
        Hashes using sha256$salt$hash (same format as the main app).
        """
        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Hash using the same algorithm as the main app (sha256$salt$hash)
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((salt + new_password).encode('utf-8')).hexdigest()
        stored_hash = f"sha256${salt}${password_hash}"
        
        engine = get_main_app_engine()
        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    UPDATE users 
                    SET password_hash = :hash, updated_at = NOW()
                    WHERE uid = :uid
                """),
                {'hash': stored_hash, 'uid': user_id}
            )
            
            if result.rowcount == 0:
                raise ValueError("User not found")
        
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='reset_password',
            target_type='user',
            target_id=user_id,
            details={'method': 'admin_reset'},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            'success': True,
            'message': 'Password reset successfully'
        }
    
    def force_logout_user(
        self,
        user_id: int,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Force logout a user by logging the intent.
        Log-only in backoffice DB — zero writes to main app DB.
        Session invalidation relies on token expiry on the frontend.
        """
        engine = get_main_app_engine()
        with engine.connect() as conn:
            user_check = conn.execute(
                text("SELECT uid FROM users WHERE uid = :uid"),
                {'uid': user_id}
            ).fetchone()
            if not user_check:
                raise ValueError("User not found")
        
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='force_logout',
            target_type='user',
            target_id=user_id,
            details={'action': 'force_logout'},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {'success': True, 'message': 'Force logout initiated'}
    
    def disable_user_2fa(
        self,
        user_id: int,
        reason: str,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Disable 2FA for a user account.
        Single UPDATE on users table: two_factor_enabled + two_factor_secret.
        """
        engine = get_main_app_engine()
        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    UPDATE users 
                    SET two_factor_enabled = FALSE, 
                        two_factor_secret = NULL, 
                        two_factor_backup_codes = NULL,
                        two_factor_verified = FALSE,
                        updated_at = NOW()
                    WHERE uid = :uid AND two_factor_enabled = TRUE
                """),
                {'uid': user_id}
            )
            
            if result.rowcount == 0:
                raise ValueError("User not found or 2FA is not enabled")
        
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='disable_2fa',
            target_type='user',
            target_id=user_id,
            details={'reason': reason[:500]},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {'success': True, 'message': '2FA disabled for user'}
    
    def export_user_data(
        self,
        user_id: int,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export all user data for GDPR compliance.
        Pure SELECT queries — zero writes to main app DB.
        """
        engine = get_main_app_engine()
        with engine.connect() as conn:
            # Get user data
            user_result = conn.execute(
                text("""
                    SELECT uid, username, user_email, name, email_verified, 
                           profile_url, last_login, created_at, updated_at
                    FROM users WHERE uid = :uid
                """),
                {'uid': user_id}
            ).fetchone()
            
            if not user_result:
                raise ValueError("User not found")
            
            user_data = {
                'id': user_result.uid,
                'username': user_result.username,
                'email': user_result.user_email,
                'name': user_result.name,
                'email_verified': user_result.email_verified,
                'profile_url': user_result.profile_url,
                'last_login': user_result.last_login.isoformat() + 'Z' if user_result.last_login else None,
                'created_at': user_result.created_at.isoformat() + 'Z' if user_result.created_at else None,
                'updated_at': user_result.updated_at.isoformat() + 'Z' if user_result.updated_at else None,
            }
            
            # Get payment data
            payment_result = conn.execute(
                text("""
                    SELECT subscription_status, subscription_plan, subscription_start, 
                           subscription_end, trial_taken, trial_end, billing_name, billing_email,
                           payment_provider, created_at
                    FROM payment WHERE uid = :uid
                """),
                {'uid': user_id}
            ).fetchone()
            
            payment_data = None
            if payment_result:
                payment_data = {
                    'subscription_status': payment_result.subscription_status,
                    'subscription_plan': payment_result.subscription_plan,
                    'subscription_start': payment_result.subscription_start.isoformat() + 'Z' if payment_result.subscription_start else None,
                    'subscription_end': payment_result.subscription_end.isoformat() + 'Z' if payment_result.subscription_end else None,
                    'trial_taken': payment_result.trial_taken,
                    'trial_end': payment_result.trial_end.isoformat() + 'Z' if payment_result.trial_end else None,
                    'billing_name': payment_result.billing_name,
                    'billing_email': payment_result.billing_email,
                    'payment_provider': payment_result.payment_provider,
                }
            
            # Get posts count
            posts_result = conn.execute(
                text("SELECT COUNT(*) FROM post WHERE uid = :uid AND is_deleted = FALSE"),
                {'uid': user_id}
            ).scalar() or 0
            
            # Get connections count
            connections_result = conn.execute(
                text("SELECT COUNT(*) FROM connections WHERE follower_uid = :uid OR followed_uid = :uid"),
                {'uid': user_id}
            ).scalar() or 0
        
        export = {
            'exported_at': datetime.utcnow().isoformat() + 'Z',
            'user': user_data,
            'payment': payment_data,
            'stats': {
                'posts_count': posts_result,
                'connections_count': connections_result,
            }
        }
        
        # Audit log (backoffice DB only)
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='export_user_data',
            target_type='user',
            target_id=user_id,
            details={'action': 'gdpr_export'},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return export
    
    def send_user_notification(
        self,
        user_id: int,
        subject: str,
        message: str,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an admin notification to a user.
        Log-only in backoffice DB — zero writes to main app DB.
        """
        # Verify user exists (read-only)
        engine = get_main_app_engine()
        with engine.connect() as conn:
            user_check = conn.execute(
                text("SELECT uid, user_email FROM users WHERE uid = :uid"),
                {'uid': user_id}
            ).fetchone()
            if not user_check:
                raise ValueError("User not found")
        
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='send_notification',
            target_type='user',
            target_id=user_id,
            details={
                'subject': subject[:200],
                'message': message[:2000],
                'user_email': user_check.user_email
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {'success': True, 'message': 'Notification logged'}
    
    def delete_user_permanent(
        self,
        user_id: int,
        reason: str,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Permanently delete a user row from the main app database (DB ON DELETE CASCADE
        cleans related rows). Then notify the former account email via SMTP if configured.
        """
        from utils.smtp_mail import send_plain_email

        engine = get_main_app_engine()
        with engine.begin() as conn:
            row = conn.execute(
                text("DELETE FROM users WHERE uid = :uid RETURNING user_email"),
                {"uid": user_id},
            ).fetchone()
            if not row:
                raise ValueError("User not found")

            user_email = row.user_email

        self._log_admin_activity(
            admin_id=admin_id,
            action_type="delete_user",
            target_type="user",
            target_id=user_id,
            details={
                "reason": reason[:500],
                "type": "permanent_delete",
                "notified_email": user_email,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        subject = "Your ZedReq account has been deleted"
        body = (
            "Hello,\n\n"
            "Your ZedReq account associated with this email address has been permanently "
            "deleted by an administrator.\n\n"
            "If you believe this was a mistake, please contact support.\n\n"
            "— ZedReq"
        )
        email_sent = send_plain_email(user_email, subject, body) if user_email else False

        return {
            "success": True,
            "message": "User account permanently deleted",
            "email_sent": email_sent,
        }
    
    # ========================================================================
    # Financial Analytics Methods
    # ========================================================================
    
    def get_revenue_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = 'day'  # 'day', 'week', 'month'
    ) -> Dict[str, Any]:
        """Get revenue analytics from main app payment table (authoritative source)"""
        try:
            engine = get_main_app_engine()
            with engine.connect() as conn:
                # Build date filter
                date_filter = ""
                if start_date:
                    date_filter += f" AND payment_date >= '{start_date.isoformat()}'"
                if end_date:
                    date_filter += f" AND payment_date <= '{end_date.isoformat()}'"
                
                # Group by period
                if group_by == 'day':
                    period_expr = "DATE(payment_date)"
                elif group_by == 'week':
                    period_expr = "DATE_TRUNC('week', payment_date)"
                elif group_by == 'month':
                    period_expr = "DATE_TRUNC('month', payment_date)"
                else:
                    period_expr = "DATE(payment_date)"
                
                # Query payment table for revenue data
                revenue_query = text(f"""
                    SELECT 
                        {period_expr} as period,
                        SUM(amount) as total,
                        COUNT(*) as count
                    FROM payment
                    WHERE amount IS NOT NULL 
                      AND amount > 0
                      AND subscription_status = 'active'
                      {date_filter}
                    GROUP BY {period_expr}
                    ORDER BY period
                """)
                
                revenue_results = conn.execute(revenue_query).fetchall()
                
                revenue_data = []
                total_revenue = 0.0
                total_transactions = 0
                
                for row in revenue_results:
                    period = row.period
                    total = float(row.total or 0.0)
                    count = row.count or 0
                    
                    revenue_data.append({
                        'period': str(period),
                        'total': total,
                        'count': count
                    })
                    total_revenue += total
                    total_transactions += count
                
                return {
                    'revenue_by_period': revenue_data,
                    'total_revenue': total_revenue,
                    'total_transactions': total_transactions
                }
        except Exception as e:
            logger.error(f"Error getting revenue analytics from main app: {e}", exc_info=True)
            # Fallback to empty data
            return {
                'revenue_by_period': [],
                'total_revenue': 0.0,
                'total_transactions': 0
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
        """Get cash flow analysis using FinancialTrackingService"""
        try:
            from services.financial_tracking_service import FinancialTrackingService
            from models.orm.user_payment_summary import UserPaymentSummary
            
            financial_service = FinancialTrackingService(self.db)
            
            # Check if payment summaries exist, if not, try to sync
            summary_count = self.db.query(UserPaymentSummary).count()
            if summary_count == 0:
                logger.info("No payment summaries found, attempting to sync...")
                try:
                    financial_service.sync_user_payment_summary(user_id=None)
                    logger.info("Payment summaries synced successfully")
                except Exception as sync_error:
                    logger.warning(f"Could not sync payment summaries: {sync_error}")
            
            # Use the new financial tracking service for accurate profit calculation
            profit_data = financial_service.calculate_net_profit(start_date, end_date)
            
            # Format response to match expected structure
            return {
                'revenue': {
                    'total_revenue': profit_data['total_revenue'],
                    'revenue_by_period': []  # Can be populated if needed
                },
                'costs': {
                    'total_costs': profit_data['total_costs'],
                    'costs_by_category': [
                        {
                            'category': 'Tavus Sessions',
                            'total': profit_data['tavus_costs']['total_cost'],
                            'count': profit_data['tavus_costs']['total_sessions']
                        }
                    ] + [
                        {
                            'category': cost['cost_name'],
                            'total': cost['amount'],
                            'count': 1
                        }
                        for cost in profit_data['fixed_costs']['costs']
                    ]
                },
                'net_cash_flow': profit_data['net_profit'],
                'profit_margin': profit_data['profit_margin']
            }
        except Exception as e:
            logger.error(f"Error getting cash flow from FinancialTrackingService: {e}", exc_info=True)
            # Fallback to old method if new service fails
            revenue_data = self.get_revenue_analytics(start_date, end_date, 'day')
            cost_data = self.get_cost_analytics(start_date, end_date)
            total_revenue = revenue_data['total_revenue']
            total_costs = cost_data['total_costs']
            net_cash_flow = total_revenue - total_costs
            
            return {
                'revenue': revenue_data,
                'costs': cost_data,
                'net_cash_flow': net_cash_flow,
                'profit_margin': (net_cash_flow / total_revenue * 100) if total_revenue > 0 else 0.0
            }
    
    def _get_main_app_user_data(self) -> Dict[str, Any]:
        """Query main app database for user and subscription data with payment amounts"""
        try:
            engine = get_main_app_engine()
            with engine.connect() as conn:
                # Get total users count
                total_users_result = conn.execute(text("SELECT COUNT(*) FROM users"))
                total_users = total_users_result.scalar() or 0
                
                # Get subscription data by plan with payment amounts
                subscription_query = text("""
                    SELECT 
                        COALESCE(subscription_plan, 'free') as plan,
                        COUNT(*) as total_count,
                        COUNT(CASE WHEN subscription_status = 'active' THEN 1 END) as active_count,
                        SUM(CASE WHEN subscription_status = 'active' AND amount IS NOT NULL THEN amount ELSE 0 END) as total_revenue,
                        AVG(CASE WHEN subscription_status = 'active' AND amount IS NOT NULL THEN amount ELSE NULL END) as avg_amount
                    FROM payment
                    GROUP BY subscription_plan
                """)
                subscription_results = conn.execute(subscription_query).fetchall()
                
                plans_breakdown = {}
                total_paid = 0
                total_revenue = 0.0
                for row in subscription_results:
                    plan = row.plan or 'free'
                    total_count = row.total_count or 0
                    active_count = row.active_count or 0
                    plan_revenue = float(row.total_revenue or 0.0)
                    avg_amount = float(row.avg_amount or 0.0)
                    
                    plans_breakdown[plan] = {
                        'total': total_count,
                        'active': active_count,
                        'revenue': plan_revenue,
                        'avg_amount': avg_amount
                    }
                    if plan != 'free' and active_count > 0:
                        total_paid += active_count
                        total_revenue += plan_revenue
                
                # Get free users (users without payment record or with free plan)
                free_users = total_users - total_paid
                
                return {
                    'total_users': total_users,
                    'paid_users': total_paid,
                    'free_users': max(0, free_users),
                    'total_revenue': total_revenue,
                    'plans_breakdown': plans_breakdown
                }
        except Exception as e:
            logger.error(f"Error querying main app database: {e}", exc_info=True)
            # Return defaults if main app DB is unavailable
            return {
                'total_users': 0,
                'paid_users': 0,
                'free_users': 0,
                'total_revenue': 0.0,
                'plans_breakdown': {}
            }
    
    def get_subscription_metrics(self) -> Dict[str, Any]:
        """Get subscription metrics from main app payment table (authoritative source)"""
        # Get data from main app database (payment table is source of truth)
        main_app_data = self._get_main_app_user_data()
        
        # Calculate MRR (Monthly Recurring Revenue) from payment amounts
        # Use actual payment amounts from payment table, not hardcoded prices
        mrr = 0.0
        plans_breakdown = main_app_data.get('plans_breakdown', {}).copy()
        
        # Calculate MRR from actual payment amounts in the payment table
        for plan, data in plans_breakdown.items():
            if plan != 'free' and data.get('active', 0) > 0:
                # If we have revenue data, use it; otherwise calculate from active count * avg amount
                plan_revenue = data.get('revenue', 0.0)
                if plan_revenue > 0:
                    mrr += plan_revenue
                else:
                    # Fallback: use average amount if available
                    avg_amount = data.get('avg_amount', 0.0)
                    if avg_amount > 0:
                        mrr += avg_amount * data.get('active', 0)
        
        total_users = main_app_data.get('total_users', 0)
        paid_users = main_app_data.get('paid_users', 0)
        free_users = main_app_data.get('free_users', 0)
        total_revenue = main_app_data.get('total_revenue', 0.0)
        
        return {
            'total_users': total_users,
            'paid_users': paid_users,
            'free_users': free_users,
            'active_subscriptions': paid_users,  # Use paid_users from payment table
            'plans_breakdown': plans_breakdown,
            'mrr': mrr,
            'total_revenue': total_revenue,
            'conversion_rate': (paid_users / total_users * 100) if total_users > 0 else 0.0
        }
    
    def get_trial_conversion_analytics(self) -> Dict[str, Any]:
        """Get trial conversion analytics from main app database"""
        try:
            engine = get_main_app_engine()
            with engine.connect() as conn:
                # Get trial data
                trial_query = text("""
                    SELECT 
                        COUNT(*) as trial_taken,
                        COUNT(CASE WHEN trial_taken = TRUE AND subscription_status = 'inactive' 
                                   AND (trial_end IS NULL OR trial_end < NOW()) THEN 1 END) as trial_not_converted,
                        COUNT(CASE WHEN trial_taken = TRUE AND subscription_status = 'active' THEN 1 END) as trial_converted
                    FROM payment
                    WHERE trial_taken = TRUE
                """)
                trial_result = conn.execute(trial_query).fetchone()
                
                trial_taken = trial_result[0] or 0 if trial_result else 0
                trial_not_converted = trial_result[1] or 0 if trial_result else 0
                trial_converted = trial_result[2] or 0 if trial_result else 0
                
                # Get time series data for trial conversions (last 90 days)
                time_series_query = text("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as trial_started,
                        COUNT(CASE WHEN subscription_status = 'active' THEN 1 END) as converted,
                        COUNT(CASE WHEN subscription_status = 'inactive' 
                                   AND (trial_end IS NULL OR trial_end < NOW()) THEN 1 END) as not_converted
                    FROM payment
                    WHERE trial_taken = TRUE
                      AND created_at >= NOW() - INTERVAL '90 days'
                    GROUP BY DATE(created_at)
                    ORDER BY DATE(created_at)
                """)
                time_series_results = conn.execute(time_series_query).fetchall()
                
                time_series = []
                for row in time_series_results:
                    date_obj = row.date
                    time_series.append({
                        'date': date_obj.isoformat() if date_obj else None,
                        'trial_started': row.trial_started or 0,
                        'converted': row.converted or 0,
                        'not_converted': row.not_converted or 0
                    })
                
                conversion_rate = (trial_converted / trial_taken * 100) if trial_taken > 0 else 0.0
                
                return {
                    'trial_taken': trial_taken,
                    'trial_converted': trial_converted,
                    'trial_not_converted': trial_not_converted,
                    'conversion_rate': conversion_rate,
                    'time_series': time_series
                }
        except Exception as e:
            logger.error(f"Error getting trial conversion analytics: {e}", exc_info=True)
            return {
                'trial_taken': 0,
                'trial_converted': 0,
                'trial_not_converted': 0,
                'conversion_rate': 0.0,
                'time_series': []
            }
    
    def get_revenue_over_time(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = 'day'  # 'day', 'week', 'month'
    ) -> List[Dict[str, Any]]:
        """Get revenue over time from main app payment table with proper ISO timestamp formatting"""
        try:
            engine = get_main_app_engine()
            with engine.connect() as conn:
                # Build date filter
                date_filter = ""
                if start_date:
                    date_filter += f" AND payment_date >= '{start_date.isoformat()}'"
                if end_date:
                    date_filter += f" AND payment_date <= '{end_date.isoformat()}'"
                
                # Group by period
                if group_by == 'day':
                    period_expr = "DATE(payment_date)"
                elif group_by == 'week':
                    period_expr = "DATE_TRUNC('week', payment_date)"
                elif group_by == 'month':
                    period_expr = "DATE_TRUNC('month', payment_date)"
                else:
                    period_expr = "DATE(payment_date)"
                
                # Query payment table for revenue data
                revenue_query = text(f"""
                    SELECT 
                        {period_expr} as period,
                        SUM(amount) as total,
                        COUNT(*) as count
                    FROM payment
                    WHERE amount IS NOT NULL 
                      AND amount > 0
                      AND subscription_status = 'active'
                      {date_filter}
                    GROUP BY {period_expr}
                    ORDER BY period
                """)
                
                revenue_results = conn.execute(revenue_query).fetchall()
                
                # Format with ISO timestamps
                result = []
                for row in revenue_results:
                    period_date = row.period
                    if isinstance(period_date, datetime):
                        timestamp = period_date.isoformat() + 'Z'
                    elif hasattr(period_date, 'isoformat'):
                        timestamp = period_date.isoformat() + 'Z'
                    else:
                        # If it's a date, convert to datetime at midnight UTC
                        if hasattr(period_date, 'strftime'):
                            timestamp = datetime.combine(period_date, datetime.min.time()).isoformat() + 'Z'
                        else:
                            timestamp = str(period_date) + 'T00:00:00Z'
                    
                    result.append({
                        'timestamp': timestamp,
                        'date': period_date.isoformat() if hasattr(period_date, 'isoformat') else str(period_date),
                        'revenue': float(row.total or 0.0),
                        'transactions': row.count or 0
                    })
                
                return result
        except Exception as e:
            logger.error(f"Error getting revenue over time from main app: {e}", exc_info=True)
            return []
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary with all key metrics including DevOps analytics"""
        # Get last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Financial metrics - use new FinancialTrackingService
        try:
            from services.financial_tracking_service import FinancialTrackingService
            from models.orm.user_payment_summary import UserPaymentSummary
            
            financial_service = FinancialTrackingService(self.db)
            
            # Check if payment summaries exist, if not, try to sync
            summary_count = self.db.query(UserPaymentSummary).count()
            if summary_count == 0:
                logger.info("No payment summaries found in dashboard, attempting to sync...")
                try:
                    financial_service.sync_user_payment_summary(user_id=None)
                    logger.info("Payment summaries synced successfully for dashboard")
                except Exception as sync_error:
                    logger.warning(f"Could not sync payment summaries: {sync_error}")
            
            # Get profit data from new system
            profit_data = financial_service.calculate_net_profit(start_date, end_date)
            
            # Format costs for dashboard
            costs_by_category = [
                {
                    'category': 'Tavus Sessions',
                    'total': profit_data['tavus_costs']['total_cost'],
                    'count': profit_data['tavus_costs']['total_sessions']
                }
            ] + [
                {
                    'category': cost['cost_name'],
                    'total': cost['amount'],
                    'count': 1
                }
                for cost in profit_data['fixed_costs']['costs']
            ]
            
            # Use new financial data
            revenue_data = {
                'total_revenue': profit_data['total_revenue'],
                'total_transactions': 0  # Can be calculated if needed
            }
            cost_data = {
                'total_costs': profit_data['total_costs'],
                'costs_by_category': costs_by_category
            }
            cash_flow = {
                'net_cash_flow': profit_data['net_profit'],
                'profit_margin': profit_data['profit_margin']
            }
        except Exception as e:
            logger.warning(f"Error using FinancialTrackingService, falling back to old method: {e}", exc_info=True)
            # Fallback to old method
            revenue_data = self.get_revenue_analytics(start_date, end_date, 'day')
            cost_data = self.get_cost_analytics(start_date, end_date)
            cash_flow = self.get_cash_flow(start_date, end_date)
        
        subscription_metrics = self.get_subscription_metrics()
        revenue_over_time = self.get_revenue_over_time(start_date, end_date, 'day')
        trial_conversion = self.get_trial_conversion_analytics()
        
        # DevOps metrics (from AnalyticsService)
        try:
            from services.analytics_service import AnalyticsService
            analytics_service = AnalyticsService(self.db)
            
            # Get uptime metrics
            uptime_metrics = analytics_service.get_uptime_metrics(days=30)
            
            # Get infrastructure metrics (last 24 hours)
            infrastructure_metrics = analytics_service.get_infrastructure_metrics(hours=24)
            
            # Get API performance metrics
            performance_metrics = analytics_service.get_api_performance(hours=24)
            
            # Get user analytics
            user_analytics = analytics_service.get_user_analytics(days=30)
            
            # Get error analytics
            error_analytics = analytics_service.get_error_analytics(days=7)
            
        except Exception as e:
            logger.error(f"Error getting DevOps metrics: {e}", exc_info=True)
            uptime_metrics = {}
            infrastructure_metrics = {}
            performance_metrics = {}
            user_analytics = {}
            error_analytics = {}
        
        # Recent transactions (last 10)
        recent_revenue = self.db.query(RevenueTransaction).filter(
            RevenueTransaction.status == 'completed'
        ).order_by(desc(RevenueTransaction.created_at)).limit(10).all()
        
        recent_costs = self.db.query(CostTransaction).order_by(
            desc(CostTransaction.created_at)
        ).limit(10).all()
        
        # Format timestamps in ISO format
        def format_timestamp(dt):
            if dt is None:
                return None
            if isinstance(dt, datetime):
                return dt.isoformat() + 'Z'
            return str(dt)
        
        return {
            'revenue': {
                'total': revenue_data['total_revenue'],
                'transactions': revenue_data['total_transactions'],
                'over_time': revenue_over_time
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
            'trial_conversion': trial_conversion,
            'devops': {
                'uptime': uptime_metrics,
                'infrastructure': infrastructure_metrics,
                'performance': performance_metrics,
                'users': user_analytics,
                'errors': error_analytics
            },
            'recent_revenue': [
                {
                    **r.to_dict(),
                    'created_at': format_timestamp(r.created_at),
                    'completed_at': format_timestamp(r.completed_at)
                }
                for r in recent_revenue
            ],
            'recent_costs': [
                {
                    **c.to_dict(),
                    'created_at': format_timestamp(c.created_at)
                }
                for c in recent_costs
            ]
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

    # ========================================================================
    # Enterprise Plan Assignment
    # ========================================================================

    def assign_enterprise_plan(
        self,
        user_email: str,
        admin_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assign enterprise plan to a user by email (payment-first).
        Only callable by super_admin via backoffice.
        
        Looks up user in main app DB by email, then:
        1. UPSERT payment (source of truth).
        2. UPSERT user_subscriptions (synced, used for quota reads).
        3. SET payment.subscription_id FK link.
        """
        # 1. Find user by email in main app
        engine = get_main_app_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT uid, username, user_email, name FROM users WHERE user_email = :email"),
                {'email': user_email.strip().lower()}
            )
            user_row = result.fetchone()

        if not user_row:
            raise ValueError(f"No user found with email: {user_email}")

        user_id = user_row[0]
        username = user_row[1]

        # 2. Find enterprise plan in main app
        with engine.connect() as conn:
            plan_result = conn.execute(
                text("SELECT plan_id FROM subscription_plans WHERE plan_name = 'enterprise' AND is_active = TRUE")
            )
            plan_row = plan_result.fetchone()

        if not plan_row:
            raise ValueError("Enterprise plan not found in database. Ensure subscription plans are seeded.")

        enterprise_plan_id = plan_row[0]

        # 3. UPSERT payment FIRST (source of truth), then sync user_subscriptions
        with engine.begin() as conn:
            # 3a. UPSERT payment FIRST (source of truth)
            pay_result = conn.execute(
                text("""
                    UPDATE payment
                    SET subscription_plan = 'enterprise', subscription_status = 'active', updated_at = NOW()
                    WHERE uid = :uid
                """),
                {'uid': user_id}
            )
            if pay_result.rowcount == 0:
                conn.execute(
                    text("""
                        INSERT INTO payment (uid, subscription_plan, subscription_status,
                                             payment_provider, created_at, updated_at)
                        VALUES (:uid, 'enterprise', 'active', 'admin_override', NOW(), NOW())
                    """),
                    {'uid': user_id}
                )
            
            # 3b. UPSERT user_subscriptions (synced from payment, used for quota reads)
            existing = conn.execute(
                text("SELECT subscription_id FROM user_subscriptions WHERE user_id = :uid"),
                {'uid': user_id}
            ).fetchone()

            if existing:
                conn.execute(
                    text("""
                        UPDATE user_subscriptions
                        SET plan_id = :plan_id, status = 'active', assigned_by = 'admin',
                            started_at = NOW(), expires_at = NULL, updated_at = NOW()
                        WHERE user_id = :uid
                    """),
                    {'plan_id': enterprise_plan_id, 'uid': user_id}
                )
                subscription_id = existing[0]
            else:
                result = conn.execute(
                    text("""
                        INSERT INTO user_subscriptions (user_id, plan_id, status, assigned_by, started_at, created_at, updated_at)
                        VALUES (:uid, :plan_id, 'active', 'admin', NOW(), NOW(), NOW())
                        RETURNING subscription_id
                    """),
                    {'uid': user_id, 'plan_id': enterprise_plan_id}
                )
                subscription_id = result.fetchone()[0]
            
            # 3c. SET payment.subscription_id FK link
            conn.execute(
                text("UPDATE payment SET subscription_id = :sub_id WHERE uid = :uid"),
                {'sub_id': subscription_id, 'uid': user_id}
            )

        # 4. Audit log
        self._log_admin_activity(
            admin_id=admin_id,
            action_type='enterprise_plan_assigned',
            target_type='user',
            target_id=user_id,
            details={
                'user_email': user_email,
                'username': username,
                'plan': 'enterprise'
            },
            ip_address=ip_address,
            user_agent=user_agent
        )

        logger.info(f"Enterprise plan assigned to user {user_email} (uid={user_id}) by admin {admin_id}")

        return {
            "success": True,
            "message": f"Enterprise plan assigned to {user_email}",
            "user_id": user_id,
            "username": username,
            "plan": "enterprise"
        }
