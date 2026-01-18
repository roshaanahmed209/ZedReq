"""Connection Service - Connection request management"""
from typing import List, Dict, Any, Optional
import asyncio

from models.user import User
from models.connection import Connection
from models.connection_request import ConnectionRequest
from models.notification import Notification
from websocket.manager import connection_manager


class ConnectionService:
    """Connection request management service"""
    
    def __init__(self, db):
        self.db = db
        self.user_model = User(db)
        self.connection_model = Connection(db)
        self.request_model = ConnectionRequest(db)
        self.notification_model = Notification(db)
    
    def send_request(self, sender_id: int, receiver_id: int, message: str = None) -> Dict[str, Any]:
        """Send a connection request"""
        # Check if receiver exists
        receiver = self.user_model.find_by_id(receiver_id)
        if not receiver:
            raise LookupError("User not found")
        
        # Check if already connected
        if self.connection_model.are_connected(sender_id, receiver_id):
            raise ValueError("Already connected with this user")
        
        # Check for existing pending request
        existing = self.request_model.find_pending_between_users(sender_id, receiver_id)
        if existing:
            raise ValueError("A pending connection request already exists")
        
        # Create the request
        request = self.request_model.create(sender_id, receiver_id, message)
        if not request:
            raise Exception("Failed to create connection request")
        
        # Get sender info for notification
        sender = self.user_model.find_by_id(sender_id)
        
        # Create notification for receiver
        self.notification_model.create(
            user_id=receiver_id,
            notification_type="connection_request",
            title="New Connection Request",
            message=f"{sender['name']} wants to connect with you",
            related_user_id=sender_id,
            related_request_id=request['id']
        )
        
        # Send real-time notification via WebSocket
        self._send_websocket_notification(
            user_id=receiver_id,
            notification_type="connection_request",
            title="New Connection Request",
            message=f"{sender['name']} wants to connect with you",
            data={
                "request_id": request['id'],
                "sender": {
                    "id": sender['id'],
                    "username": sender['username'],
                    "name": sender['name'],
                    "profile_pic": sender.get('profile_pic')
                }
            }
        )
        
        return self._format_request(request, sender=sender, receiver=receiver)
    
    def accept_request(self, request_id: int, receiver_id: int) -> Dict[str, Any]:
        """Accept a connection request"""
        # Get the request
        request = self.request_model.find_by_id(request_id)
        if not request:
            raise LookupError("Connection request not found")
        
        # Verify the receiver is correct
        if request['receiver_id'] != receiver_id:
            raise PermissionError("You cannot accept this request")
        
        # Check if already accepted
        if request['status'] != 'pending':
            raise ValueError(f"Request is already {request['status']}")
        
        # Update request status
        self.request_model.update_status(request_id, 'accepted')
        
        # Create bidirectional connection
        sender_id = request['sender_id']
        self.connection_model.create_bidirectional(sender_id, receiver_id)
        
        # Get user info
        sender = self.user_model.find_by_id(sender_id)
        receiver = self.user_model.find_by_id(receiver_id)
        
        # Create notification for sender
        self.notification_model.create(
            user_id=sender_id,
            notification_type="connection_accepted",
            title="Connection Accepted",
            message=f"{receiver['name']} accepted your connection request",
            related_user_id=receiver_id
        )
        
        # Send real-time notification
        self._send_websocket_notification(
            user_id=sender_id,
            notification_type="connection_accepted",
            title="Connection Accepted",
            message=f"{receiver['name']} accepted your connection request",
            data={
                "user": {
                    "id": receiver['id'],
                    "username": receiver['username'],
                    "name": receiver['name'],
                    "profile_pic": receiver.get('profile_pic')
                }
            }
        )
        
        # Return the new connection
        connections = self.connection_model.get_user_connections(receiver_id)
        for conn in connections:
            if conn['user_id'] == sender_id:
                return {
                    "id": conn['id'],
                    "user_id": receiver_id,
                    "connected_user_id": sender_id,
                    "connected_user": {
                        "id": sender['id'],
                        "username": sender['username'],
                        "name": sender['name'],
                        "profile_pic": sender.get('profile_pic')
                    },
                    "connected_at": conn['connected_at']
                }
        
        raise Exception("Failed to create connection")
    
    def reject_request(self, request_id: int, receiver_id: int) -> None:
        """Reject a connection request"""
        # Get the request
        request = self.request_model.find_by_id(request_id)
        if not request:
            raise LookupError("Connection request not found")
        
        # Verify the receiver is correct
        if request['receiver_id'] != receiver_id:
            raise PermissionError("You cannot reject this request")
        
        # Check if already processed
        if request['status'] != 'pending':
            raise ValueError(f"Request is already {request['status']}")
        
        # Update request status
        self.request_model.update_status(request_id, 'rejected')
    
    def remove_connection(self, connection_id: int, user_id: int) -> None:
        """Remove an existing connection"""
        connection = self.connection_model.find_by_id(connection_id)
        if not connection:
            raise LookupError("Connection not found")
        
        # Verify user is part of this connection
        if connection['follower_uid'] != user_id:
            raise PermissionError("You cannot remove this connection")
        
        # Remove bidirectional connection
        other_user_id = connection['followed_uid']
        success = self.connection_model.remove_connection(user_id, other_user_id)
        
        if not success:
            raise Exception("Failed to remove connection")
    
    def get_pending_requests(self, user_id: int) -> List[Dict[str, Any]]:
        """Get pending requests received by user"""
        requests = self.request_model.get_pending_received(user_id)
        return [self._format_received_request(req) for req in requests]
    
    def get_sent_requests(self, user_id: int) -> List[Dict[str, Any]]:
        """Get requests sent by user"""
        requests = self.request_model.get_pending_sent(user_id)
        return [self._format_sent_request(req) for req in requests]
    
    def _format_request(self, request: Dict[str, Any], sender: Dict = None, receiver: Dict = None) -> Dict[str, Any]:
        """Format request for response"""
        result = {
            "id": request['id'],
            "sender_id": request['sender_id'],
            "receiver_id": request['receiver_id'],
            "status": request['status'],
            "message": request.get('message'),
            "created_at": request['created_at'],
            "updated_at": request.get('updated_at')
        }
        
        if sender:
            result["sender"] = {
                "id": sender['id'],
                "username": sender['username'],
                "name": sender['name'],
                "profile_pic": sender.get('profile_pic')
            }
        
        if receiver:
            result["receiver"] = {
                "id": receiver['id'],
                "username": receiver['username'],
                "name": receiver['name'],
                "profile_pic": receiver.get('profile_pic')
            }
        
        return result
    
    def _format_received_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Format received request with sender info"""
        return {
            "id": request['id'],
            "sender_id": request['sender_id'],
            "receiver_id": request['receiver_id'],
            "status": request['status'],
            "message": request.get('message'),
            "sender": {
                "id": request['sender_user_id'],
                "username": request['sender_username'],
                "name": request['sender_name'],
                "profile_pic": request.get('sender_profile_pic')
            },
            "created_at": request['created_at'],
            "updated_at": request.get('updated_at')
        }
    
    def _format_sent_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Format sent request with receiver info"""
        return {
            "id": request['id'],
            "sender_id": request['sender_id'],
            "receiver_id": request['receiver_id'],
            "status": request['status'],
            "message": request.get('message'),
            "receiver": {
                "id": request['receiver_user_id'],
                "username": request['receiver_username'],
                "name": request['receiver_name'],
                "profile_pic": request.get('receiver_profile_pic')
            },
            "created_at": request['created_at'],
            "updated_at": request.get('updated_at')
        }
    
    def _send_websocket_notification(
        self, 
        user_id: int, 
        notification_type: str, 
        title: str, 
        message: str,
        data: dict = None
    ):
        """Send real-time notification via WebSocket (fire and forget)"""
        try:
            asyncio.create_task(
                connection_manager.send_notification(
                    user_id=user_id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    data=data
                )
            )
        except RuntimeError:
            # No event loop running (sync context) - skip WebSocket notification
            pass
