"""Payment Model - PCI Compliant"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS payment (
    pay_id SERIAL PRIMARY KEY,
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    
    -- Payment provider info (Stripe/PayPal tokens - NEVER store raw card numbers)
    payment_provider VARCHAR(50) NOT NULL DEFAULT 'stripe',
    provider_customer_id VARCHAR(255),
    provider_payment_method_id VARCHAR(255),
    
    -- Card display info only (last 4 digits for display)
    card_last_four CHAR(4),
    card_brand VARCHAR(20),
    card_exp_month INTEGER,
    card_exp_year INTEGER,
    
    -- Billing info
    billing_name VARCHAR(100),
    billing_email VARCHAR(150),
    
    -- Subscription status
    subscription_status VARCHAR(50) DEFAULT 'inactive',
    subscription_plan VARCHAR(50),
    subscription_start TIMESTAMP,
    subscription_end TIMESTAMP,
    
    -- Trial info
    trial_taken BOOLEAN DEFAULT FALSE,
    trial_end TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_payment_uid ON payment(uid)',
    'CREATE INDEX IF NOT EXISTS idx_payment_provider_customer ON payment(provider_customer_id)',
    'CREATE INDEX IF NOT EXISTS idx_payment_status ON payment(subscription_status)'
]


class Payment(BaseModel):
    """Payment model - stores payment method references (not actual card data)"""
    table_name = 'payment'
    
    def create(self, uid: int, provider: str = 'stripe', **kwargs) -> Optional[Dict[str, Any]]:
        """
        Create a payment record with provider tokens
        
        Args:
            uid: User ID
            provider: Payment provider (stripe, paypal, etc.)
            **kwargs: provider_customer_id, provider_payment_method_id, 
                     card_last_four, card_brand, billing_name, etc.
        
        Returns:
            Created payment record
        """
        return self.db.execute_returning(
            '''INSERT INTO payment (
                   uid, payment_provider, provider_customer_id, provider_payment_method_id,
                   card_last_four, card_brand, card_exp_month, card_exp_year,
                   billing_name, billing_email
               ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
               RETURNING *''',
            (uid, provider, 
             kwargs.get('provider_customer_id'),
             kwargs.get('provider_payment_method_id'),
             kwargs.get('card_last_four'),
             kwargs.get('card_brand'),
             kwargs.get('card_exp_month'),
             kwargs.get('card_exp_year'),
             kwargs.get('billing_name'),
             kwargs.get('billing_email'))
        )
    
    def get_by_user(self, uid: int) -> Optional[Dict[str, Any]]:
        """Get user's payment info"""
        return self.db.fetch_one(
            'SELECT * FROM payment WHERE uid = %s', (uid,)
        )
    
    def update_payment_method(self, pay_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update payment method from provider"""
        return self.db.execute_returning(
            '''UPDATE payment SET 
               provider_payment_method_id = COALESCE(%s, provider_payment_method_id),
               card_last_four = COALESCE(%s, card_last_four),
               card_brand = COALESCE(%s, card_brand),
               card_exp_month = COALESCE(%s, card_exp_month),
               card_exp_year = COALESCE(%s, card_exp_year),
               updated_at = CURRENT_TIMESTAMP
               WHERE pay_id = %s RETURNING *''',
            (kwargs.get('provider_payment_method_id'),
             kwargs.get('card_last_four'),
             kwargs.get('card_brand'),
             kwargs.get('card_exp_month'),
             kwargs.get('card_exp_year'),
             pay_id)
        )
    
    def activate_subscription(self, pay_id: int, plan: str, end_date=None) -> Optional[Dict[str, Any]]:
        """Activate a subscription"""
        return self.db.execute_returning(
            '''UPDATE payment SET 
               subscription_status = 'active',
               subscription_plan = %s,
               subscription_start = CURRENT_TIMESTAMP,
               subscription_end = %s,
               updated_at = CURRENT_TIMESTAMP
               WHERE pay_id = %s RETURNING *''',
            (plan, end_date, pay_id)
        )
    
    def cancel_subscription(self, pay_id: int) -> Optional[Dict[str, Any]]:
        """Cancel a subscription"""
        return self.db.execute_returning(
            '''UPDATE payment SET 
               subscription_status = 'cancelled',
               updated_at = CURRENT_TIMESTAMP
               WHERE pay_id = %s RETURNING *''',
            (pay_id,)
        )
    
    def start_trial(self, pay_id: int, trial_days: int = 14) -> Optional[Dict[str, Any]]:
        """Start a trial period"""
        return self.db.execute_returning(
            '''UPDATE payment SET 
               trial_taken = TRUE,
               trial_end = CURRENT_TIMESTAMP + INTERVAL '%s days',
               subscription_status = 'trial',
               updated_at = CURRENT_TIMESTAMP
               WHERE pay_id = %s AND trial_taken = FALSE
               RETURNING *''',
            (trial_days, pay_id)
        )
    
    def is_subscription_active(self, uid: int) -> bool:
        """Check if user has active subscription or trial"""
        result = self.db.fetch_one(
            '''SELECT 1 FROM payment 
               WHERE uid = %s AND (
                   subscription_status = 'active' 
                   OR (subscription_status = 'trial' AND trial_end > CURRENT_TIMESTAMP)
               )''',
            (uid,)
        )
        return result is not None
