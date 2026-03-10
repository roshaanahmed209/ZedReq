"""Seed database with initial data for backoffice system"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from config.database_orm import SessionLocal, init_orm_tables
from models.orm.admin_user import AdminUser
from models.orm.revenue_transaction import RevenueTransaction
from models.orm.cost_transaction import CostTransaction
from models.orm.financial_summary import FinancialSummary
from models.orm.admin_activity_log import AdminActivityLog
from models.orm.bearable_cost import BearableCost
from services.auth_service import AuthService
from services.financial_service import FinancialService
from utils.auth import hash_password
from datetime import datetime, timedelta, date
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial bootstrap admin (bypasses reserved-username check; only used in seed)
INITIAL_ADMIN_USERNAME = "admin"
INITIAL_ADMIN_EMAIL = "admin@zedreq.com"
INITIAL_ADMIN_PASSWORD = "roshaan_admin_zed"  # Change in production after first login


def create_initial_admin(db: Session):
    """Create initial super_admin user (direct ORM to allow reserved username 'admin')."""
    try:
        existing = db.query(AdminUser).filter(AdminUser.username == INITIAL_ADMIN_USERNAME).first()
        if existing:
            logger.info("Admin user already exists, skipping creation")
            return existing.to_dict()

        admin_user = AdminUser(
            username=INITIAL_ADMIN_USERNAME,
            email=INITIAL_ADMIN_EMAIL,
            password_hash=hash_password(INITIAL_ADMIN_PASSWORD),
            role="super_admin",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        logger.info("✓ Initial super_admin user created")
        logger.warning("⚠ Default login: %s / %s - CHANGE PASSWORD IN PRODUCTION!", INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_PASSWORD)
        return admin_user.to_dict()
    except Exception as e:
        logger.error("Error creating admin user: %s", e, exc_info=True)
        db.rollback()
        raise


def generate_sample_revenue_transactions(db: Session, count: int = 50):
    """Generate sample revenue transactions"""
    try:
        financial_service = FinancialService(db)
        
        transaction_types = ['subscription', 'one_time', 'refund']
        plans = ['free', 'pro', 'premium']
        providers = ['stripe', 'paypal', 'manual']
        statuses = ['completed', 'pending', 'failed']
        
        base_date = datetime.utcnow() - timedelta(days=90)
        
        for i in range(count):
            transaction_type = random.choice(transaction_types)
            plan_type = random.choice(plans) if transaction_type == 'subscription' else None
            
            # Amount based on plan
            if plan_type == 'pro':
                amount = 29.99
            elif plan_type == 'premium':
                amount = 99.99
            else:
                amount = random.uniform(10.0, 500.0)
            
            created_at = base_date + timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            transaction = RevenueTransaction(
                user_id=random.randint(1, 100) if random.random() > 0.3 else None,
                transaction_type=transaction_type,
                amount=amount,
                currency='USD',
                plan_type=plan_type,
                provider=random.choice(providers),
                provider_transaction_id=f"txn_{random.randint(100000, 999999)}",
                status=random.choice(statuses),
                description=f"Sample {transaction_type} transaction",
                extra_metadata={'sample': True, 'generated_at': datetime.utcnow().isoformat()},
                created_at=created_at,
                completed_at=created_at if random.random() > 0.2 else None
            )
            
            db.add(transaction)
        
        db.commit()
        logger.info(f"✓ Generated {count} sample revenue transactions")
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating revenue transactions: {e}", exc_info=True)
        raise


def generate_sample_cost_transactions(db: Session, count: int = 100):
    """Generate sample cost transactions"""
    try:
        financial_service = FinancialService(db)
        
        categories = ['openai', 'tavus', 'infrastructure', 'storage', 'other']
        openai_models = ['gpt-4o-mini', 'text-embedding-3-large', 'gpt-4']
        services = {
            'openai': openai_models,
            'tavus': ['tavus-api'],
            'infrastructure': ['database', 'server', 'cdn'],
            'storage': ['cloudflare-r2', 'backup'],
            'other': ['email', 'sms', 'monitoring']
        }
        
        base_date = datetime.utcnow() - timedelta(days=90)
        
        for i in range(count):
            category = random.choice(categories)
            service_name = random.choice(services.get(category, ['service']))
            
            # Cost ranges by category
            if category == 'openai':
                amount = random.uniform(0.001, 5.0)
                quantity = random.randint(100, 100000)
            elif category == 'tavus':
                amount = random.uniform(0.50, 2.0)
                quantity = 1
            elif category == 'infrastructure':
                amount = random.uniform(10.0, 200.0)
                quantity = None
            elif category == 'storage':
                amount = random.uniform(1.0, 50.0)
                quantity = random.uniform(10.0, 1000.0)
            else:
                amount = random.uniform(0.10, 20.0)
                quantity = None
            
            created_at = base_date + timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            transaction = CostTransaction(
                cost_category=category,
                service_name=service_name,
                amount=amount,
                currency='USD',
                unit_type='token' if category == 'openai' else 'request' if category == 'tavus' else 'gb' if category == 'storage' else 'monthly',
                quantity=quantity,
                user_id=random.randint(1, 100) if random.random() > 0.5 else None,
                extra_metadata={
                    'sample': True,
                    'generated_at': datetime.utcnow().isoformat(),
                    'category': category
                },
                created_at=created_at
            )
            
            db.add(transaction)
        
        db.commit()
        logger.info(f"✓ Generated {count} sample cost transactions")
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating cost transactions: {e}", exc_info=True)
        raise


def generate_financial_summaries(db: Session):
    """Generate financial summaries for last 6 months"""
    try:
        financial_service = FinancialService(db)
        
        today = date.today()
        
        # Generate monthly summaries for last 6 months
        for i in range(6):
            month_start = date(today.year, today.month, 1) - timedelta(days=30 * i)
            if month_start.month == 1:
                month_end = date(month_start.year, 12, 31)
            else:
                month_end = date(month_start.year, month_start.month, 1) - timedelta(days=1)
            
            # Adjust for current month
            if i == 0:
                month_end = today
            
            try:
                summary = financial_service.generate_financial_summary(
                    period_type='monthly',
                    period_start=month_start,
                    period_end=month_end
                )
                logger.info(f"✓ Generated summary for {month_start.strftime('%Y-%m')}")
            except Exception as e:
                logger.warning(f"Could not generate summary for {month_start}: {e}")
        
        logger.info("✓ Generated financial summaries")
    except Exception as e:
        logger.error(f"Error generating financial summaries: {e}", exc_info=True)


def generate_sample_activity_logs(db: Session, count: int = 30):
    """Generate sample activity logs"""
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == 'admin').first()
        if not admin:
            logger.warning("No admin user found, skipping activity logs")
            return
        
        action_types = [
            'login', 'user_role_update', 'user_suspend', 'user_delete',
            'revenue_create', 'cost_create', 'financial_summary_generate'
        ]
        target_types = ['user', 'transaction', 'summary', None]
        
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for i in range(count):
            action_type = random.choice(action_types)
            target_type = random.choice(target_types) if action_type != 'login' else None
            
            created_at = base_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            log = AdminActivityLog(
                admin_id=admin.id,
                action_type=action_type,
                target_type=target_type,
                target_id=random.randint(1, 100) if target_type else None,
                details={'sample': True, 'action': action_type},
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (Sample Browser)",
                created_at=created_at
            )
            
            db.add(log)
        
        db.commit()
        logger.info(f"✓ Generated {count} sample activity logs")
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating activity logs: {e}", exc_info=True)
        raise


def seed_bearable_costs(db: Session):
    """Seed initial bearable costs data"""
    try:
        # Check if costs already exist
        existing = db.query(BearableCost).count()
        if existing > 0:
            logger.info("Bearable costs already exist, skipping seed")
            return
        
        # Tavus Session cost (per session)
        tavus_cost = BearableCost(
            cost_name="Tavus Session",
            amount=0.25,
            is_fixed=False,
            unit_type="session"
        )
        db.add(tavus_cost)
        
        # Hosting + Database cost (fixed monthly)
        hosting_cost = BearableCost(
            cost_name="Hosting + Database",
            amount=25.00,
            is_fixed=True,
            unit_type="month"
        )
        db.add(hosting_cost)
        
        db.commit()
        logger.info("✓ Seeded bearable costs: Tavus Session ($0.25/session), Hosting + Database ($25/month)")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding bearable costs: {e}", exc_info=True)
        raise


def seed_all():
    """Seed all data"""
    logger.info("Starting database seeding...")
    
    # Initialize ORM tables
    init_orm_tables()
    
    db = SessionLocal()
    try:
        # Create initial admin
        create_initial_admin(db)
        
        # Seed bearable costs (must be done before other operations)
        seed_bearable_costs(db)
        
        # Generate sample data
        generate_sample_revenue_transactions(db, count=50)
        generate_sample_cost_transactions(db, count=100)
        generate_financial_summaries(db)
        generate_sample_activity_logs(db, count=30)
        
        logger.info("✓ Database seeding completed successfully")
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed_all()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        sys.exit(1)
