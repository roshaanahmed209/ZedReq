"""Network Service - User discovery and suggestions using ORM"""
from typing import List, Dict, Any
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from models.orm import User, Connection, Description


class NetworkService:
    """Network discovery and suggestions service using ORM"""
    
    def __init__(self, db: Session):
        self.db = db

    def are_users_connected(self, user_id: int, other_user_id: int) -> bool:
        """True if a Connection exists between the two users (either direction)."""
        conn = (
            self.db.query(Connection)
            .filter(
                or_(
                    and_(Connection.follower_uid == user_id, Connection.followed_uid == other_user_id),
                    and_(Connection.follower_uid == other_user_id, Connection.followed_uid == user_id),
                )
            )
            .first()
        )
        return conn is not None
    
    def get_discover_users(self, current_user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get random 20% of users for discovery.
        Excludes:
        - Current user
        - Already connected users (from connections table)
        """
        # Get 20% of total users, minimum 1
        total_users = self.db.query(func.count(User.uid)).scalar()
        discovery_limit = max(1, min(limit, int(total_users * 0.2)))
        
        # Get connected user IDs (bidirectional)
        followed_uids = [
            row[0] for row in self.db.query(Connection.followed_uid)
            .filter(Connection.follower_uid == current_user_id)
            .all()
        ]
        follower_uids = [
            row[0] for row in self.db.query(Connection.follower_uid)
            .filter(Connection.followed_uid == current_user_id)
            .all()
        ]
        connected_uids = set(followed_uids + follower_uids)
        
        # Get random users excluding current user and connected users
        query = (
            self.db.query(User)
            .outerjoin(Description, User.description_id == Description.desc_id)
            .filter(User.uid != current_user_id)
        )
        
        if connected_uids:
            query = query.filter(~User.uid.in_(list(connected_uids)))
        
        users = (
            query
            .order_by(func.random())
            .limit(discovery_limit)
            .all()
        )
        
        return [self._format_user(user) for user in users]
    
    def get_suggestions(self, current_user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get friend-of-friend suggestions.
        Returns users connected to your connections, ranked by mutual connection count.
        """
        # Get user's connections (bidirectional)
        my_connections = (
            self.db.query(Connection.followed_uid.label('conn_id'))
            .filter(Connection.follower_uid == current_user_id)
            .union(
                self.db.query(Connection.follower_uid.label('conn_id'))
                .filter(Connection.followed_uid == current_user_id)
            )
            .subquery()
        )
        
        # Get suggested users with mutual connection count
        # This is a complex query - we'll use a simpler approach with ORM
        # Get all connections of my connections
        suggested_users = {}
        
        # Get my connection IDs
        my_conn_ids = [row[0] for row in self.db.query(my_connections.c.conn_id).all()]
        
        if not my_conn_ids:
            return []
        
        # For each of my connections, get their connections
        for conn_id in my_conn_ids:
            # Get users that this connection follows or is followed by
            their_connections = (
                self.db.query(Connection)
                .filter(
                    or_(
                        Connection.follower_uid == conn_id,
                        Connection.followed_uid == conn_id
                    )
                )
                .all()
            )
            
            for conn in their_connections:
                other_user_id = conn.followed_uid if conn.follower_uid == conn_id else conn.follower_uid
                
                # Skip if it's me or already connected
                if other_user_id == current_user_id or other_user_id in my_conn_ids:
                    continue
                
                if other_user_id not in suggested_users:
                    suggested_users[other_user_id] = {
                        'user_id': other_user_id,
                        'mutual_connections': 0,
                        'mutual_names': []
                    }
                
                suggested_users[other_user_id]['mutual_connections'] += 1
                # Get mutual connection name
                mutual_user = self.db.query(User).filter(User.uid == conn_id).first()
                if mutual_user and mutual_user.name:
                    if mutual_user.name not in suggested_users[other_user_id]['mutual_names']:
                        suggested_users[other_user_id]['mutual_names'].append(mutual_user.name)
        
        # Sort by mutual connections and get top results
        sorted_suggestions = sorted(
            suggested_users.values(),
            key=lambda x: x['mutual_connections'],
            reverse=True
        )[:limit]
        
        # Get full user details
        result = []
        for suggestion in sorted_suggestions:
            user = (
                self.db.query(User)
                .outerjoin(Description, User.description_id == Description.desc_id)
                .filter(User.uid == suggestion['user_id'])
                .first()
            )
            
            if user:
                formatted = self._format_user(user)
                formatted['mutual_connections'] = suggestion['mutual_connections']
                formatted['mutual_connection_names'] = suggestion['mutual_names'][:3]
                result.append(formatted)
        
        return result
    
    def get_user_connections(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's accepted connections"""
        # Get bidirectional connections
        connections = (
            self.db.query(Connection)
            .filter(
                or_(
                    Connection.follower_uid == user_id,
                    Connection.followed_uid == user_id
                )
            )
            .order_by(desc(Connection.connected_at))
            .all()
        )
        
        # Get unique user IDs
        connected_user_ids = set()
        for conn in connections:
            if conn.follower_uid == user_id:
                connected_user_ids.add(conn.followed_uid)
            else:
                connected_user_ids.add(conn.follower_uid)
        
        # Get user details
        users = (
            self.db.query(User)
            .outerjoin(Description, User.description_id == Description.desc_id)
            .filter(User.uid.in_(connected_user_ids))
            .all()
        )
        
        return [self._format_user(user) for user in users]
    
    def _format_user(self, user: User) -> Dict[str, Any]:
        """Format user data for response"""
        # Get description if available
        profile_pic = None
        short_desc = None
        skills = None
        current_status = None
        
        if user.description_id:
            desc = (
                self.db.query(Description)
                .filter(Description.desc_id == user.description_id)
                .first()
            )
            if desc:
                profile_pic = desc.profile_pic
                short_desc = desc.short_desc
                skills = desc.skills
                current_status = desc.current_status
        
        return {
            "id": user.uid,
            "uid": user.uid,
            "username": user.username,
            "name": user.name,
            "profile_pic": profile_pic,
            "short_desc": short_desc,
            "current_status": current_status,
            "skills": skills
        }
    
    def _format_suggested_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Format suggested user with mutual connections"""
        formatted = self._format_user(user)
        formatted["mutual_connections"] = user.get("mutual_connections", 0)
        mutual_names = user.get("mutual_names") or []
        # Limit to first 3 names
        formatted["mutual_connection_names"] = mutual_names[:3] if mutual_names else []
        return formatted
