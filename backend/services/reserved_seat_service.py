"""Reserved Seat Service"""
import random
import string
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.orm.reserved_seat import ReservedSeat
from models.orm.user import User
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ReservedSeatService:
    """Service for managing reserved seats"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_promo_code(self, email: str) -> str:
        """
        Generate promo code from email
        Format: first 4 letters of email + underscore + 4 random digits
        Example: firstuser@gmail.com -> firs_7892
        """
        # Get first 4 letters from email (before @)
        email_prefix = email.split('@')[0].lower()[:4]
        
        # Generate 4 random digits
        random_digits = ''.join(random.choices(string.digits, k=4))
        
        # Combine: first4letters_4digits
        promo_code = f"{email_prefix}_{random_digits}"
        
        return promo_code
    
    def reserve_seat(self, email: str, user_id: int = None) -> dict:
        """
        Reserve a seat for a user
        
        Args:
            email: User's email address
            user_id: Optional user ID if user is logged in
            
        Returns:
            Dictionary with success status, message, and promo code
        """
        # Check if email already exists
        existing_reservation = self.db.query(ReservedSeat).filter(
            ReservedSeat.email == email.lower()
        ).first()
        
        if existing_reservation:
            logger.info(f"Email already reserved | Email: {email[:3]}*** | Promo Code: {existing_reservation.promo_code}")
            logger.info(f"⚠ No email sent - reservation already exists. User should check their previous email.")
            return {
                "success": True,
                "message": "You've already reserved your seat! Check your email for your promo code.",
                "promo_code": existing_reservation.promo_code,
                "already_reserved": True
            }
        
        # If user_id is provided, verify user exists
        if user_id:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                user_id = None  # User doesn't exist, proceed without user_id
        
        # Generate unique promo code with retry logic
        # Use database constraint to ensure uniqueness (avoid TOCTOU race condition)
        max_retries = 10
        reservation = None
        
        for attempt in range(max_retries):
            # Generate promo code
            promo_code = self.generate_promo_code(email)
            
            # Create reservation - let database enforce uniqueness
            reservation = ReservedSeat(
                email=email.lower(),
                user_id=user_id,
                promo_code=promo_code
            )
            
            try:
                self.db.add(reservation)
                self.db.commit()
                self.db.refresh(reservation)
                # Success - break out of retry loop
                break
            except IntegrityError as e:
                self.db.rollback()
                
                # Check if it's a duplicate email error (not promo code)
                error_str = str(e.orig).lower() if hasattr(e, 'orig') else str(e).lower()
                
                if "email" in error_str or ("unique" in error_str and "email" in error_str):
                    # Email was reserved between check and insert (race condition)
                    existing_reservation = self.db.query(ReservedSeat).filter(
                        ReservedSeat.email == email.lower()
                    ).first()
                    if existing_reservation:
                        logger.info(f"Email already reserved (race condition detected): {email[:3]}***")
                        return {
                            "success": True,
                            "message": "You've already reserved your seat! Check your email for your promo code.",
                            "promo_code": existing_reservation.promo_code,
                            "already_reserved": True
                        }
                
                # If it's a promo code collision, retry with new code
                if "promo_code" in error_str or ("unique" in error_str and "promo_code" in error_str):
                    logger.debug(f"Promo code collision on attempt {attempt + 1}, regenerating...")
                    if attempt == max_retries - 1:
                        # Last attempt failed
                        logger.error("Failed to generate unique promo code after multiple attempts")
                        raise ValueError("Unable to generate unique reservation code. Please try again.")
                    # Continue to next iteration to retry
                    continue
                
                # Unknown integrity error
                logger.error(f"Database integrity error during reservation: {type(e).__name__}")
                raise ValueError("Unable to complete reservation. Please try again later.")
        else:
            # This should not happen due to raise in loop, but safety check
            logger.error("Failed to create reservation after all retries")
            raise ValueError("Unable to complete reservation. Please try again later.")
        
        # Email is now sent from frontend using EmailJS client-side SDK
        # Backend only stores the reservation and returns the promo code
        logger.info(f"✓ Reservation completed successfully | ID: {reservation.id} | Promo Code: {promo_code} | Email will be sent from frontend")
        
        return {
            "success": True,
            "message": "Seat reserved successfully! Check your email for your promo code.",
            "promo_code": promo_code,
            "already_reserved": False
        }
    
    def get_reservation_by_email(self, email: str) -> ReservedSeat | None:
        """Get reservation by email"""
        return self.db.query(ReservedSeat).filter(
            ReservedSeat.email == email.lower()
        ).first()
    
    def get_reservation_by_promo_code(self, promo_code: str) -> ReservedSeat | None:
        """Get reservation by promo code"""
        return self.db.query(ReservedSeat).filter(
            ReservedSeat.promo_code == promo_code
        ).first()
