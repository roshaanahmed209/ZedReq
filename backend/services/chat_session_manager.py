"""
Chat Session Manager - Session-based conversation management with isolation
Implements OWASP security practices and scalability considerations
"""
import time
import uuid
import logging
from typing import Dict, List, Optional, Tuple
from threading import Lock
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class ChatSession:
    """Represents a single chat session with conversation history"""
    
    def __init__(self, session_id: str, user_id: int, created_at: float = None):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = created_at or time.time()
        self.last_activity = self.created_at
        self.conversation_history: List[Dict[str, str]] = []
        self.message_count = 0
        self.lock = Lock()  # Thread-safe access
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history (thread-safe)"""
        with self.lock:
            self.conversation_history.append({
                "role": role,
                "content": content
            })
            self.message_count += 1
            self.last_activity = time.time()
    
    def get_history(self, max_messages: int = 50) -> List[Dict[str, str]]:
        """Get conversation history (thread-safe, limited to prevent context overflow)"""
        with self.lock:
            # Return last N messages to prevent context overflow
            return self.conversation_history[-max_messages:]
    
    def clear_history(self) -> None:
        """Clear conversation history (thread-safe)"""
        with self.lock:
            self.conversation_history.clear()
            self.message_count = 0
    
    def is_expired(self, timeout_seconds: int = 3600) -> bool:
        """Check if session has expired (default 1 hour)"""
        return (time.time() - self.last_activity) > timeout_seconds
    
    def get_age_seconds(self) -> float:
        """Get session age in seconds"""
        return time.time() - self.created_at


class ChatSessionManager:
    """
    Manages chat sessions with proper isolation and security
    
    Features:
    - Session isolation per user (no context leakage)
    - Automatic session expiration and cleanup
    - Thread-safe operations
    - Memory-efficient (in-memory, can be swapped for Redis)
    - OWASP security practices
    """
    
    def __init__(
        self,
        session_timeout_seconds: int = 3600,  # 1 hour default
        max_sessions_per_user: int = 5,  # Limit concurrent sessions per user
        cleanup_interval_seconds: int = 300,  # Cleanup every 5 minutes
        max_history_per_session: int = 50  # Max messages per session
    ):
        self.sessions: Dict[str, ChatSession] = {}  # session_id -> ChatSession
        self.user_sessions: Dict[int, List[str]] = {}  # user_id -> [session_ids]
        self.session_timeout = session_timeout_seconds
        self.max_sessions_per_user = max_sessions_per_user
        self.cleanup_interval = cleanup_interval_seconds
        self.max_history = max_history_per_session
        self.lock = Lock()  # Thread-safe access to session dict
        self.last_cleanup = time.time()
        
        logger.info(
            f"ChatSessionManager initialized: "
            f"timeout={session_timeout_seconds}s, "
            f"max_sessions_per_user={max_sessions_per_user}, "
            f"cleanup_interval={cleanup_interval_seconds}s"
        )
    
    def create_session(self, user_id: int) -> str:
        """
        Create a new chat session for a user
        
        Args:
            user_id: User ID
            
        Returns:
            session_id: Unique session identifier
        """
        with self.lock:
            # Cleanup expired sessions periodically
            self._cleanup_expired_sessions_if_needed()
            
            # Limit concurrent sessions per user
            user_session_ids = self.user_sessions.get(user_id, [])
            active_sessions = [
                sid for sid in user_session_ids
                if sid in self.sessions and not self.sessions[sid].is_expired(self.session_timeout)
            ]
            
            if len(active_sessions) >= self.max_sessions_per_user:
                # Remove oldest session
                oldest_session_id = min(
                    active_sessions,
                    key=lambda sid: self.sessions[sid].created_at
                )
                self._remove_session(oldest_session_id)
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Create new session
            session = ChatSession(session_id, user_id)
            self.sessions[session_id] = session
            
            # Track user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)
            
            logger.info(f"Created chat session {session_id} for user {user_id}")
            return session_id
    
    def get_session(self, session_id: str, user_id: int) -> Optional[ChatSession]:
        """
        Get a session by ID with user validation (prevents session hijacking)
        
        Args:
            session_id: Session identifier
            user_id: User ID for validation
            
        Returns:
            ChatSession if valid and belongs to user, None otherwise
        """
        with self.lock:
            session = self.sessions.get(session_id)
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
            
            # Security: Verify session belongs to user (prevent session hijacking)
            if session.user_id != user_id:
                logger.warning(
                    f"Session hijacking attempt: session {session_id} "
                    f"belongs to user {session.user_id}, not {user_id}"
                )
                return None
            
            # Check if expired
            if session.is_expired(self.session_timeout):
                logger.info(f"Session {session_id} expired, removing")
                self._remove_session(session_id)
                return None
            
            return session
    
    def add_message(
        self,
        session_id: str,
        user_id: int,
        role: str,
        content: str
    ) -> bool:
        """
        Add a message to a session's conversation history
        
        Args:
            session_id: Session identifier
            user_id: User ID for validation
            role: Message role ('user' or 'assistant')
            content: Message content (should be sanitized)
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id, user_id)
        if not session:
            return False
        
        session.add_message(role, content)
        return True
    
    def get_history(
        self,
        session_id: str,
        user_id: int,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            user_id: User ID for validation
            max_messages: Maximum number of messages to return (default: configured max)
            
        Returns:
            List of conversation messages
        """
        session = self.get_session(session_id, user_id)
        if not session:
            return []
        
        limit = max_messages or self.max_history
        return session.get_history(limit)
    
    def remove_session(self, session_id: str, user_id: int) -> bool:
        """
        Remove a session (user must own it)
        
        Args:
            session_id: Session identifier
            user_id: User ID for validation
            
        Returns:
            True if removed, False otherwise
        """
        session = self.get_session(session_id, user_id)
        if not session:
            return False
        
        with self.lock:
            self._remove_session(session_id)
        
        logger.info(f"Removed chat session {session_id} for user {user_id}")
        return True
    
    def _remove_session(self, session_id: str) -> None:
        """Internal method to remove session (assumes lock is held)"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        user_id = session.user_id
        
        # Remove from sessions dict
        del self.sessions[session_id]
        
        # Remove from user_sessions tracking
        if user_id in self.user_sessions:
            self.user_sessions[user_id] = [
                sid for sid in self.user_sessions[user_id] if sid != session_id
            ]
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
    
    def _cleanup_expired_sessions_if_needed(self) -> None:
        """Cleanup expired sessions periodically (assumes lock is held)"""
        current_time = time.time()
        if (current_time - self.last_cleanup) < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]
        
        for session_id in expired_sessions:
            self._remove_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired chat sessions")
    
    def cleanup_expired_sessions(self) -> int:
        """
        Manually trigger cleanup of expired sessions
        
        Returns:
            Number of sessions cleaned up
        """
        with self.lock:
            expired_sessions = [
                sid for sid, session in self.sessions.items()
                if session.is_expired(self.session_timeout)
            ]
            
            for session_id in expired_sessions:
                self._remove_session(session_id)
            
            self.last_cleanup = time.time()
            
            if expired_sessions:
                logger.info(f"Manually cleaned up {len(expired_sessions)} expired chat sessions")
            
            return len(expired_sessions)
    
    def get_stats(self) -> Dict[str, any]:
        """Get session manager statistics"""
        with self.lock:
            return {
                "total_sessions": len(self.sessions),
                "total_users": len(self.user_sessions),
                "sessions_per_user": {
                    user_id: len(session_ids)
                    for user_id, session_ids in self.user_sessions.items()
                }
            }


# Global session manager instance
_session_manager: Optional[ChatSessionManager] = None


def get_session_manager() -> ChatSessionManager:
    """Get or create global session manager instance"""
    global _session_manager
    
    if _session_manager is None:
        import os
        _session_manager = ChatSessionManager(
            session_timeout_seconds=int(os.environ.get('CHAT_SESSION_TIMEOUT', 3600)),
            max_sessions_per_user=int(os.environ.get('CHAT_MAX_SESSIONS_PER_USER', 5)),
            cleanup_interval_seconds=int(os.environ.get('CHAT_CLEANUP_INTERVAL', 300)),
            max_history_per_session=int(os.environ.get('CHAT_MAX_HISTORY', 50))
        )
    
    return _session_manager
