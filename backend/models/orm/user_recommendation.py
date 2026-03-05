"""User Recommendation ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User


class UserRecommendation(Base):
    """SQLAlchemy ORM model for user_recommendations table"""
    __tablename__ = 'user_recommendations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    recommender_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    relationship_type = Column('relationship', String(100))  # Maps Python attr to DB column 'relationship'
    recommendation_text = Column(Text, nullable=False)
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        backref="recommendations_received"
    )
    recommender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[recommender_id],
        backref="recommendations_given"
    )
    
    def __repr__(self):
        return f"<UserRecommendation(id={self.id}, user_id={self.user_id}, recommender_id={self.recommender_id})>"
    
    def to_dict(self, include_recommender_info=False):
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'recommender_id': self.recommender_id,
            'relationship': self.relationship_type,  # Map to 'relationship' in API response for backward compatibility
            'relationship_type': self.relationship_type,
            'recommendation_text': self.recommendation_text,
            'is_visible': self.is_visible,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_recommender_info and self.recommender:
            result['recommender'] = {
                'id': self.recommender.uid,
                'username': self.recommender.username,
                'name': self.recommender.name
            }
        
        return result
