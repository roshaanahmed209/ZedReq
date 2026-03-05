"""Connection Model - Uses existing connections table with follower_uid/followed_uid"""
from typing import Optional, Dict, Any, List
from .base import BaseModel


class Connection(BaseModel):
    """Connection model using existing connections table (follower_uid/followed_uid)"""
    table_name = 'connections'
    
    def create(self, follower_uid: int, followed_uid: int) -> Optional[Dict[str, Any]]:
        """Create a connection (one direction)"""
        return self.db.execute_returning(
            '''INSERT INTO connections (follower_uid, followed_uid)
               VALUES (%s, %s)
               ON CONFLICT (follower_uid, followed_uid) DO NOTHING
               RETURNING *''',
            (follower_uid, followed_uid)
        )
    
    def create_bidirectional(self, user1_id: int, user2_id: int) -> bool:
        """Create connections in both directions (mutual connection)"""
        self.db.execute(
            '''INSERT INTO connections (follower_uid, followed_uid)
               VALUES (%s, %s), (%s, %s)
               ON CONFLICT (follower_uid, followed_uid) DO NOTHING''',
            (user1_id, user2_id, user2_id, user1_id)
        )
        return True
    
    def find_by_id(self, connection_id: int) -> Optional[Dict[str, Any]]:
        """Find connection by ID"""
        return self.db.fetch_one(
            'SELECT * FROM connections WHERE connection_id = %s',
            (connection_id,)
        )
    
    def are_connected(self, user1_id: int, user2_id: int) -> bool:
        """Check if two users are connected"""
        result = self.db.fetch_one(
            '''SELECT 1 FROM connections 
               WHERE (follower_uid = %s AND followed_uid = %s)
                  OR (follower_uid = %s AND followed_uid = %s)''',
            (user1_id, user2_id, user2_id, user1_id)
        )
        return result is not None
    
    def get_user_connections(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all connections for a user with user info"""
        return self.db.fetch_all(
            '''SELECT c.connection_id as id, c.connected_at,
                      u.uid as user_id, u.username, u.name, 
                      d.profile_pic, d.short_desc, d.skills, d.current_status
               FROM connections c
               JOIN users u ON c.followed_uid = u.uid
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE c.follower_uid = %s
               ORDER BY c.connected_at DESC''',
            (user_id,)
        )
    
    def get_connection_ids(self, user_id: int) -> List[int]:
        """Get list of connected user IDs"""
        results = self.db.fetch_all(
            'SELECT followed_uid FROM connections WHERE follower_uid = %s',
            (user_id,)
        )
        return [r['followed_uid'] for r in results]
    
    def get_connection_count(self, user_id: int) -> int:
        """Get total number of connections for a user"""
        result = self.db.fetch_one(
            'SELECT COUNT(*) as count FROM connections WHERE follower_uid = %s',
            (user_id,)
        )
        return result['count'] if result else 0
    
    def remove_connection(self, user1_id: int, user2_id: int) -> bool:
        """Remove connection between two users (both directions)"""
        cursor = self.db.execute(
            '''DELETE FROM connections 
               WHERE (follower_uid = %s AND followed_uid = %s)
                  OR (follower_uid = %s AND followed_uid = %s)''',
            (user1_id, user2_id, user2_id, user1_id)
        )
        return cursor.rowcount > 0
    
    def remove_by_id(self, connection_id: int, user_id: int) -> bool:
        """Remove a specific connection if user owns it"""
        conn = self.find_by_id(connection_id)
        if not conn:
            return False
        
        if conn['follower_uid'] != user_id:
            return False
        
        return self.remove_connection(user_id, conn['followed_uid'])
    
    def get_mutual_connections(self, user1_id: int, user2_id: int) -> List[Dict[str, Any]]:
        """Get mutual connections between two users"""
        return self.db.fetch_all(
            '''SELECT u.uid as id, u.username, u.name, d.profile_pic
               FROM users u
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE u.uid IN (
                   SELECT c1.followed_uid 
                   FROM connections c1
                   WHERE c1.follower_uid = %s
                   INTERSECT
                   SELECT c2.followed_uid 
                   FROM connections c2
                   WHERE c2.follower_uid = %s
               )''',
            (user1_id, user2_id)
        )
    
    def get_following(self, user_id: int) -> List[Dict[str, Any]]:
        """Get list of users that this user follows"""
        return self.db.fetch_all(
            'SELECT followed_uid FROM connections WHERE follower_uid = %s',
            (user_id,)
        )
    
    def get_followers(self, user_id: int) -> List[Dict[str, Any]]:
        """Get list of users that follow this user"""
        return self.db.fetch_all(
            'SELECT follower_uid FROM connections WHERE followed_uid = %s',
            (user_id,)
        )
