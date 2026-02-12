"""
User ORM Model - SQLAlchemy ORM version
This replaces the raw SQL User model in models/user.py
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base


class User(Base):
    """SQLAlchemy ORM model for users table"""
    __tablename__ = 'users'
    
    uid = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    name = Column(String(100), nullable=False)
    user_email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(100))
    description_id = Column(Integer)
    pay_id = Column(Integer)
    job_id = Column(Integer)
    profile_url = Column(Text)  # Profile URL in format: {API_URL}/profile/{username}-{hashed_user_id}
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships (if needed in future)
    # connections: Mapped[list["Connection"]] = relationship(...)
    # posts: Mapped[list["Post"]] = relationship(...)
    
    def __repr__(self):
        return f"<User(uid={self.uid}, username='{self.username}')>"
    
    def to_dict(self, include_password=False):
        """Convert to dictionary, excluding sensitive data by default"""
        data = {
            'id': self.uid,  # Normalized to 'id'
            'uid': self.uid,
            'username': self.username,
            'name': self.name,
            'email': self.user_email,  # Normalized to 'email'
            'user_email': self.user_email,
            'email_verified': self.email_verified,
            'description_id': self.description_id,
            'profile_url': self.profile_url,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
        
        return data