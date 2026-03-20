"""
Setup Test Subscription Accounts - Randomly assigns subscription plans to all users

This script:
1. Queries all existing users from the database
2. Randomly assigns subscription plans (free, pro, premium, enterprise)
3. Sets up payment table entries (payment-first architecture)
4. Sets up user_subscriptions entries (synced from payment)
5. Sets usage_tracking to limit-1 for each feature (AI messages, course enrollments, interviews)

Usage:
    python backend/scripts/setup_test_subscriptions.py
"""

import os
import sys
import random
from datetime import datetime, timezone, date

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_orm import SessionLocal, engine
from models.orm.user import User
from models.orm.payment import Payment
from models.orm.subscription_plan import SubscriptionPlan
from models.orm.user_subscription import UserSubscription
from models.orm.usage_tracking import UsageTracking
from services.subscription_service import SubscriptionService

# Available plans (with weighted distribution for realistic testing)
# free: 40%, pro: 35%, premium: 20%, enterprise: 5%
PLAN_WEIGHTS = {
    "free": 0.40,
    "pro": 0.35,
    "premium": 0.20,
    "enterprise": 0.05,
}

# Admin emails to exclude (don't modify admin accounts)
ADMIN_EMAILS = ["admin@roshaan.com", "admin@zedrec.com"]

# Plan limits (from subscription_service.py)
PLAN_LIMITS = {
    "free": {
        "ai_messages_per_month": 30,
        "course_enrollments_per_month": 2,
        "interview_sessions_per_month": 1,
    },
    "pro": {
        "ai_messages_per_month": 100,
        "course_enrollments_per_month": 3,
        "interview_sessions_per_month": 3,
    },
    "premium": {
        "ai_messages_per_month": 500,
        "course_enrollments_per_month": 5,
        "interview_sessions_per_month": 5,
    },
    "enterprise": {
        "ai_messages_per_month": -1,  # unlimited
        "course_enrollments_per_month": -1,
        "interview_sessions_per_month": -1,
    },
}

# Plan prices (for payment amounts)
PLAN_PRICES = {
    "free": 0.00,
    "pro": 49.99,
    "premium": 89.99,
    "enterprise": 199.99,
}


def get_random_plan() -> str:
    """Randomly select a plan based on weighted distribution"""
    plans = list(PLAN_WEIGHTS.keys())
    weights = list(PLAN_WEIGHTS.values())
    return random.choices(plans, weights=weights, k=1)[0]


def get_current_period_start() -> date:
    """Get the 1st day of the current UTC month"""
    today = datetime.now(timezone.utc).date()
    return today.replace(day=1)


def setup_user_subscription(db: SessionLocal, user: User, plan_name: str) -> dict:
    """
    Set up subscription for a user (payment-first architecture).
    Returns user_id and subscription_id.
    """
    print(f"  Processing: {user.username} ({user.user_email}) → {plan_name} plan")
    subscription_status = "active" if plan_name != "free" else "inactive"

    # 1. Ensure subscription_plans are seeded
    plan_obj = db.query(SubscriptionPlan).filter_by(plan_name=plan_name, is_active=True).first()
    if not plan_obj:
        print(f"  ⚠ Plan '{plan_name}' not found. Seeding plans...")
        svc = SubscriptionService(db)
        svc.seed_plans(db)
        plan_obj = db.query(SubscriptionPlan).filter_by(plan_name=plan_name, is_active=True).first()
        if not plan_obj:
            raise ValueError(f"Failed to seed plan '{plan_name}'")

    # 2. UPSERT payment FIRST (payment-first architecture)
    payment_amount = PLAN_PRICES.get(plan_name, 0.00)
    payment_date = datetime.now(timezone.utc) if subscription_status == 'active' else None
    
    payment = db.query(Payment).filter(Payment.uid == user.uid).first()
    if payment:
        payment.subscription_plan = plan_name
        payment.subscription_status = subscription_status
        payment.payment_provider = "random_assignment_script"
        # Update payment amount and dates
        if subscription_status == 'active' and plan_name != 'free':
            payment.amount = payment_amount
            payment.currency = 'USD'
            payment.payment_date = payment_date
            payment.last_payment_date = payment_date
            payment.transaction_id = f"test_{user.uid}_{int(payment_date.timestamp())}"
        payment.updated_at = datetime.now(timezone.utc)
    else:
        payment = Payment(
            uid=user.uid,
            subscription_plan=plan_name,
            subscription_status=subscription_status,
            payment_provider="random_assignment_script",
            amount=payment_amount if subscription_status == 'active' and plan_name != 'free' else None,
            currency='USD' if subscription_status == 'active' and plan_name != 'free' else None,
            payment_date=payment_date,
            last_payment_date=payment_date,
            transaction_id=f"test_{user.uid}_{int(payment_date.timestamp())}" if payment_date else None,
        )
        db.add(payment)
        db.flush()
        user.pay_id = payment.pay_id

    # 3. UPSERT user_subscriptions (synced from payment)
    user_sub = db.query(UserSubscription).filter(UserSubscription.user_id == user.uid).first()
    if user_sub:
        user_sub.plan_id = plan_obj.plan_id
        user_sub.status = subscription_status
        user_sub.assigned_by = "random_assignment_script"
        user_sub.started_at = datetime.now(timezone.utc)
        user_sub.updated_at = datetime.now(timezone.utc)
        subscription_id = user_sub.subscription_id
    else:
        user_sub = UserSubscription(
            user_id=user.uid,
            plan_id=plan_obj.plan_id,
            status=subscription_status,
            assigned_by="random_assignment_script",
            started_at=datetime.now(timezone.utc),
        )
        db.add(user_sub)
        db.flush()
        subscription_id = user_sub.subscription_id

    # 4. SET payment.subscription_id FK link
    payment.subscription_id = subscription_id
    db.flush()

    # 5. Set usage_tracking to limit-1 for each feature
    period_start = get_current_period_start()
    limits = PLAN_LIMITS[plan_name]

    features = [
        ("ai_messages", limits["ai_messages_per_month"]),
        ("course_enrollments", limits["course_enrollments_per_month"]),
        ("interview_sessions", limits["interview_sessions_per_month"]),
    ]

    for feature_name, limit in features:
        if limit == -1:
            # Enterprise unlimited - set to 0 (they can use unlimited)
            usage_count = 0
        else:
            # Set to limit-1 (one request away from quota)
            usage_count = max(0, limit - 1)

        # UPSERT usage_tracking
        usage = (
            db.query(UsageTracking)
            .filter(
                UsageTracking.user_id == user.uid,
                UsageTracking.feature == feature_name,
                UsageTracking.period_start == period_start,
            )
            .first()
        )

        if usage:
            usage.usage_count = usage_count
            usage.updated_at = datetime.now(timezone.utc)
        else:
            usage = UsageTracking(
                user_id=user.uid,
                feature=feature_name,
                period_start=period_start,
                usage_count=usage_count,
            )
            db.add(usage)

    return {
        "user_id": user.uid,
        "username": user.username,
        "email": user.user_email,
        "plan": plan_name,
        "subscription_id": subscription_id,
        "pay_id": payment.pay_id,
    }


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("RANDOM SUBSCRIPTION PLAN ASSIGNMENT")
    print("="*60)
    print("\nThis script will:")
    print("  1. Query all existing users from database")
    print("  2. Exclude admin accounts")
    print("  3. Randomly assign plans: free (40%), pro (35%), premium (20%), enterprise (5%)")
    print("  4. Set up payment table (payment-first)")
    print("  5. Set up user_subscriptions (synced)")
    print("  6. Set usage_tracking to limit-1 for each feature")
    print("\n" + "="*60)

    db = SessionLocal()
    results = []
    plan_counts = {"free": 0, "pro": 0, "premium": 0, "enterprise": 0}

    try:
        # Ensure plans are seeded
        svc = SubscriptionService(db)
        svc.seed_plans(db)
        print("✓ Subscription plans seeded\n")

        # Query all users, excluding admins
        all_users = db.query(User).all()
        users_to_process = [
            user for user in all_users
            if user.user_email.lower() not in [email.lower() for email in ADMIN_EMAILS]
        ]

        if not users_to_process:
            print("⚠ No users found to process (excluding admins)")
            return

        print(f"Found {len(users_to_process)} users to process (excluding {len(all_users) - len(users_to_process)} admin(s))\n")
        print("="*60)
        print("PROCESSING USERS")
        print("="*60)

        # Process each user with random plan assignment
        for idx, user in enumerate(users_to_process, 1):
            plan_name = get_random_plan()
            plan_counts[plan_name] += 1
            
            try:
                result = setup_user_subscription(db, user, plan_name)
                results.append(result)
                # Commit after each user for transaction safety
                db.commit()
                if idx % 10 == 0:
                    print(f"  ✓ Processed {idx}/{len(users_to_process)} users\n")
            except Exception as e:
                print(f"  ❌ Error processing {user.username}: {e}")
                db.rollback()
                continue

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"\n✓ Successfully processed {len(results)} users:\n")
        print(f"  Plan Distribution:")
        for plan, count in plan_counts.items():
            percentage = (count / len(results) * 100) if results else 0
            print(f"    • {plan:10}: {count:3} users ({percentage:5.1f}%)")
        
        print(f"\n  Sample users (first 10):")
        for r in results[:10]:
            print(f"    • {r['username']:20} | {r['email']:30} | Plan: {r['plan']:10}")
        if len(results) > 10:
            print(f"    ... and {len(results) - 10} more users")
        
        print("\n" + "="*60)
        print("TESTING INSTRUCTIONS")
        print("="*60)
        print("\n1. Check Backoffice Dashboard:")
        print("   - Navigate to Users tab")
        print("   - Verify subscription plans are randomly distributed")
        print("   - Check that payment and user_subscriptions are synced")
        print("\n2. Test Quota Gating:")
        print("   - Login as any user")
        print("   - Make ONE request to AI mode / LMS / Interview")
        print("   - Should succeed (limit-1 + 1 = limit)")
        print("   - Make ANOTHER request")
        print("   - Should fail with 403 (quota exceeded)")
        print("\n3. Test Plan Upgrade:")
        print("   - In backoffice, upgrade any user to a different plan")
        print("   - Verify payment table updated first")
        print("   - Verify user_subscriptions synced")
        print("   - Verify usage_tracking limits updated")
        print("\n4. Test Enterprise (Unlimited):")
        print("   - Find an enterprise user in backoffice")
        print("   - Login as that user")
        print("   - Make multiple requests")
        print("   - Should never hit quota (unlimited)")
        print("\n" + "="*60)

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
