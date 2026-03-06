"""Link Click ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class LinkClick(Base):
    """SQLAlchemy ORM model for link_clicks table"""
    __tablename__ = 'link_clicks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String(255), index=True)
    link_url = Column(String(1000), nullable=False, index=True)
    link_text = Column(String(500))
    page_path = Column(String(500))
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    is_external = Column(Boolean, default=False, index=True)
    
    __table_args__ = (
        Index('idx_linkclicks_user', 'user_id', 'timestamp'),
        Index('idx_linkclicks_session', 'session_id', 'timestamp'),
        Index('idx_linkclicks_url', 'link_url', 'timestamp'),
        Index('idx_linkclicks_timestamp', 'timestamp'),
        Index('idx_linkclicks_external', 'is_external', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<LinkClick(id={self.id}, user_id={self.user_id}, url='{self.link_url[:50]}...', external={self.is_external})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'link_url': self.link_url,
            'link_text': self.link_text,
            'page_path': self.page_path,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_external': self.is_external,
        }
