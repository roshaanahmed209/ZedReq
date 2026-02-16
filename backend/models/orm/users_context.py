"""Users Context ORM Model"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from config.database_orm import Base


class UsersContext(Base):
    """SQLAlchemy ORM model for users_context table"""
    __tablename__ = 'users_context'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    zed = Column(Text)  # Comprehensive user context maintained by Zed agent
    lemzy = Column(Text)  # Reserved for future Lemzy agent context
    pez = Column(Text)  # Reserved for future Pez agent context
    riz = Column(Text)  # Reserved for future Riz agent context
    runtime_context = Column(JSONB)  # Raw user activity data (JSONB)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        backref="user_context"
    )
    
    def __repr__(self):
        return f"<UsersContext(id={self.id}, user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'zed': self.zed,
            'lemzy': self.lemzy,
            'pez': self.pez,
            'riz': self.riz,
            'runtime_context': self.runtime_context,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
