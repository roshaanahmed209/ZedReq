"""WebSocket Connection Manager for Real-time Notifications"""
from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio


class ConnectionManager:
    """
    Manages WebSocket connections for real-time notifications.
    Each user can have multiple connections (multiple tabs/devices).
    """
    
    def __init__(self):
        # Map of user_id (int) -> list of WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        async with self._lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
        
        print(f"WebSocket connected: User {user_id} (total connections: {len(self.active_connections[user_id])})")
    
    def disconnect(self, user_id: int, websocket: WebSocket = None):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            if websocket:
                # Remove specific connection
                try:
                    self.active_connections[user_id].remove(websocket)
                except ValueError:
                    pass
            else:
                # Remove all connections for user (on error)
                self.active_connections[user_id] = []
            
            # Clean up if no connections left
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            print(f"WebSocket disconnected: User {user_id}")
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send a message to all connections for a specific user"""
        if user_id not in self.active_connections:
            return False
        
        message_json = json.dumps(message, default=str)
        disconnected = []
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                print(f"Failed to send to user {user_id}: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected sockets
        for ws in disconnected:
            self.disconnect(user_id, ws)
        
        return True
    
    async def send_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str = None,
        data: dict = None
    ):
        """Send a notification to a user"""
        notification = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "data": data or {}
        }
        
        return await self.send_to_user(user_id, notification)
    
    async def broadcast(self, message: dict, exclude_user: int = None):
        """Broadcast a message to all connected users"""
        message_json = json.dumps(message, default=str)
        
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            
            for websocket in connections:
                try:
                    await websocket.send_text(message_json)
                except Exception:
                    pass
    
    def is_user_online(self, user_id: int) -> bool:
        """Check if a user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_online_users(self) -> List[int]:
        """Get list of online user IDs"""
        return list(self.active_connections.keys())


# Global connection manager instance
connection_manager = ConnectionManager()
