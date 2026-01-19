"""Network Service - User discovery and suggestions"""
from typing import List, Dict, Any

from models.user import User


class NetworkService:
    """Network discovery and suggestions service"""
    
    def __init__(self, db):
        self.db = db
        self.user_model = User(db)
    
    def get_discover_users(self, current_user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get random 20% of users for discovery.
        Excludes:
        - Current user
        - Already connected users (from connections table)
        """
        # Get 20% of total users, minimum 1
        total_users = self.user_model.get_total_count()
        discovery_limit = max(1, min(limit, int(total_users * 0.2)))
        
        # Use existing connections table with follower_uid/followed_uid
        results = self.db.fetch_all(
            '''SELECT u.uid, u.username, u.name, d.profile_pic, d.short_desc, 
                      d.skills, d.current_status
               FROM users u
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE u.uid != %s
                 AND u.uid NOT IN (
                     -- Exclude already connected users (bidirectional)
                     SELECT followed_uid FROM connections WHERE follower_uid = %s
                     UNION
                     SELECT follower_uid FROM connections WHERE followed_uid = %s
                 )
               ORDER BY RANDOM()
               LIMIT %s''',
            (current_user_id, current_user_id, current_user_id, discovery_limit)
        )
        
        return [self._format_user(user) for user in results]
    
    def get_suggestions(self, current_user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get friend-of-friend suggestions.
        Returns users connected to your connections, ranked by mutual connection count.
        """
        results = self.db.fetch_all(
            '''WITH my_connections AS (
                   SELECT followed_uid AS conn_id FROM connections WHERE follower_uid = %s
                   UNION
                   SELECT follower_uid AS conn_id FROM connections WHERE followed_uid = %s
               )
               SELECT 
                   u.uid, u.username, u.name, d.profile_pic, d.short_desc, 
                   d.skills, d.current_status,
                   COUNT(DISTINCT mc.conn_id) as mutual_connections,
                   ARRAY_AGG(DISTINCT mu.name) FILTER (WHERE mu.name IS NOT NULL) as mutual_names
               FROM users u
               LEFT JOIN description d ON u.description_id = d.desc_id
               INNER JOIN connections c ON (c.follower_uid = u.uid OR c.followed_uid = u.uid)
               INNER JOIN my_connections mc ON (
                   (c.follower_uid = mc.conn_id AND c.followed_uid = u.uid) OR
                   (c.followed_uid = mc.conn_id AND c.follower_uid = u.uid)
               )
               LEFT JOIN users mu ON mu.uid = mc.conn_id
               WHERE u.uid != %s
                 AND u.uid NOT IN (SELECT conn_id FROM my_connections)
               GROUP BY u.uid, u.username, u.name, d.profile_pic, d.short_desc, 
                        d.skills, d.current_status
               ORDER BY mutual_connections DESC
               LIMIT %s''',
            (current_user_id, current_user_id, current_user_id, limit)
        )
        
        return [self._format_suggested_user(user) for user in results]
    
    def get_user_connections(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's accepted connections"""
        results = self.db.fetch_all(
            '''SELECT DISTINCT ON (u.uid) u.uid, u.username, u.name, d.profile_pic, d.short_desc,
                      d.skills, d.current_status, c.connected_at
               FROM connections c
               INNER JOIN users u ON (
                   (c.followed_uid = u.uid AND c.follower_uid = %s) OR
                   (c.follower_uid = u.uid AND c.followed_uid = %s)
               )
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE u.uid != %s
               ORDER BY u.uid, c.connected_at DESC''',
            (user_id, user_id, user_id)
        )
        return [self._format_user(conn) for conn in results]
    
    def _format_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Format user data for response"""
        return {
            "id": user.get("uid"),
            "username": user.get("username"),
            "name": user.get("name"),
            "profile_pic": user.get("profile_pic"),
            "short_desc": user.get("short_desc"),
            "current_status": user.get("current_status"),
            "skills": user.get("skills")
        }
    
    def _format_suggested_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Format suggested user with mutual connections"""
        formatted = self._format_user(user)
        formatted["mutual_connections"] = user.get("mutual_connections", 0)
        mutual_names = user.get("mutual_names") or []
        # Limit to first 3 names
        formatted["mutual_connection_names"] = mutual_names[:3] if mutual_names else []
        return formatted
