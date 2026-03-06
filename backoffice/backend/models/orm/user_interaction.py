"""User Interaction ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from config.database_orm import Base


class UserInteraction(Base):
    """SQLAlchemy ORM model for user_interactions table"""
    __tablename__ = 'user_interactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String(255), index=True)
    interaction_type = Column(String(50), nullable=False, index=True)
    element_id = Column(String(255))
    element_type = Column(String(50))
    page_path = Column(String(500))
    metadata = Column(JSONB)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_interactions_user', 'user_id', 'timestamp'),
        Index('idx_interactions_session', 'session_id', 'timestamp'),
        Index('idx_interactions_type', 'interaction_type', 'timestamp'),
        Index('idx_interactions_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<UserInteraction(id={self.id}, user_id={self.user_id}, type='{self.interaction_type}', element='{self.element_id}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'interaction_type': self.interaction_type,
            'element_id': self.element_id,
            'element_type': self.element_type,
            'page_path': self.page_path,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
