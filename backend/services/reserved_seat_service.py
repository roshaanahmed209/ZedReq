"""Reserved Seat Service"""
import random
import string
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.orm.reserved_seat import ReservedSeat
from models.orm.user import User
from utils.email_sender import send_reservation_confirmation_email


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
        
        # Generate unique promo code
        promo_code = self.generate_promo_code(email)
        
        # Ensure promo code is unique (retry if collision)
        max_retries = 10
        for _ in range(max_retries):
            existing = self.db.query(ReservedSeat).filter(
                ReservedSeat.promo_code == promo_code
            ).first()
            
            if not existing:
                break
            
            # Regenerate if collision
            promo_code = self.generate_promo_code(email)
        else:
            raise ValueError("Failed to generate unique promo code after multiple attempts")
        
        # Create reservation
        reservation = ReservedSeat(
            email=email.lower(),
            user_id=user_id,
            promo_code=promo_code
        )
        
        try:
            self.db.add(reservation)
            self.db.commit()
            self.db.refresh(reservation)
        except IntegrityError as e:
            self.db.rollback()
            # Check if it's a duplicate email error
            if "email" in str(e).lower() or "unique" in str(e).lower():
                # Email was reserved between check and insert
                existing_reservation = self.db.query(ReservedSeat).filter(
                    ReservedSeat.email == email.lower()
                ).first()
                if existing_reservation:
                    return {
                        "success": True,
                        "message": "You've already reserved your seat! Check your email for your promo code.",
                        "promo_code": existing_reservation.promo_code,
                        "already_reserved": True
                    }
            raise ValueError(f"Failed to create reservation: {str(e)}")
        
        # Send confirmation email
        email_sent = send_reservation_confirmation_email(email, promo_code)
        
        if not email_sent:
            # Email failed but reservation was created
            # Log the error but don't fail the request
            print(f"Warning: Reservation created for {email} but email failed to send")
        
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
