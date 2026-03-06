"""Page View ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class PageView(Base):
    """SQLAlchemy ORM model for page_views table"""
    __tablename__ = 'page_views'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String(255), index=True)
    page_path = Column(String(500), nullable=False, index=True)
    page_title = Column(String(255))
    referrer = Column(String(500))
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    load_time_ms = Column(Integer)
    
    __table_args__ = (
        Index('idx_pageviews_user', 'user_id', 'timestamp'),
        Index('idx_pageviews_session', 'session_id', 'timestamp'),
        Index('idx_pageviews_path', 'page_path', 'timestamp'),
        Index('idx_pageviews_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<PageView(id={self.id}, user_id={self.user_id}, path='{self.page_path}', timestamp={self.timestamp})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'page_path': self.page_path,
            'page_title': self.page_title,
            'referrer': self.referrer,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'load_time_ms': self.load_time_ms,
        }
