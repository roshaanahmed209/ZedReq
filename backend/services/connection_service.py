"""Connection Service - Connection request management using ORM"""
from typing import List, Dict, Any, Optional
import asyncio
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from models.orm import User, Connection, ConnectionRequest
from services.notification_service import NotificationService
from services.feed_cache import invalidate_feed_for_users
from websocket.manager import connection_manager


class ConnectionService:
    """Connection request management service using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
    
    def send_request(self, sender_id: int, receiver_id: int, message: str = None) -> Dict[str, Any]:
        """Send a connection request"""
        # Check if receiver exists
        receiver = self.db.query(User).filter(User.uid == receiver_id).first()
        if not receiver:
            raise LookupError("User not found")
        
        # Check if already connected
        if self._are_connected(sender_id, receiver_id):
            raise ValueError("Already connected with this user")
        
        # Check for existing pending request
        existing = (
            self.db.query(ConnectionRequest)
            .filter(
                and_(
                    ConnectionRequest.status == 'pending',
                    or_(
                        and_(
                            ConnectionRequest.sender_id == sender_id,
                            ConnectionRequest.receiver_id == receiver_id
                        ),
                        and_(
                            ConnectionRequest.sender_id == receiver_id,
                            ConnectionRequest.receiver_id == sender_id
                        )
                    )
                )
            )
            .first()
        )
        if existing:
            raise ValueError("A pending connection request already exists")
        
        # Create the request
        request = ConnectionRequest(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message,
            status='pending'
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        # Get sender info
        sender = self.db.query(User).filter(User.uid == sender_id).first()
        
        # Create notification for receiver
        self.notification_service.create_notification(
            user_id=receiver_id,
            notification_type="connection_request",
            title="New Connection Request",
            message=f"{sender.name} wants to connect with you",
            related_user_id=sender_id,
            related_request_id=request.id
        )
        
        # Send real-time notification via WebSocket
        self._send_websocket_notification(
            user_id=receiver_id,
            notification_type="connection_request",
            title="New Connection Request",
            message=f"{sender.name} wants to connect with you",
            data={
                "request_id": request.id,
                "sender": {
                    "id": sender.uid,
                    "username": sender.username,
                    "name": sender.name,
                    "profile_pic": None  # Would need description join
                }
            }
        )
        
        return self._format_request(request, sender=sender, receiver=receiver)
    
    def accept_request(self, request_id: int, receiver_id: int) -> Dict[str, Any]:
        """Accept a connection request"""
        # Get the request
        request = self.db.query(ConnectionRequest).filter(ConnectionRequest.id == request_id).first()
        if not request:
            raise LookupError("Connection request not found")
        
        # Verify the receiver is correct
        if request.receiver_id != receiver_id:
            raise PermissionError("You cannot accept this request")
        
        # Check if already accepted
        if request.status != 'pending':
            raise ValueError(f"Request is already {request.status}")
        
        # Update request status
        request.status = 'accepted'
        self.db.commit()
        
        # Create bidirectional connection
        sender_id = request.sender_id
        self._create_bidirectional_connection(sender_id, receiver_id)
        invalidate_feed_for_users(self.db, sender_id, receiver_id)

        # Get user info
        sender = self.db.query(User).filter(User.uid == sender_id).first()
        receiver = self.db.query(User).filter(User.uid == receiver_id).first()
        
        # Create notification for sender
        self.notification_service.create_notification(
            user_id=sender_id,
            notification_type="connection_accepted",
            title="Connection Accepted",
            message=f"{receiver.name} accepted your connection request",
            related_user_id=receiver_id
        )
        
        # Send real-time notification
        self._send_websocket_notification(
            user_id=sender_id,
            notification_type="connection_accepted",
            title="Connection Accepted",
            message=f"{receiver.name} accepted your connection request",
            data={
                "user": {
                    "id": receiver.uid,
                    "username": receiver.username,
                    "name": receiver.name,
                    "profile_pic": None
                }
            }
        )
        
        # Return the new connection
        connection = (
            self.db.query(Connection)
            .filter(
                and_(
                    Connection.follower_uid == receiver_id,
                    Connection.followed_uid == sender_id
                )
            )
            .first()
        )
        
        if connection:
            return {
                "id": connection.connection_id,
                "user_id": receiver_id,
                "connected_user_id": sender_id,
                "connected_user": {
                    "id": sender.uid,
                    "username": sender.username,
                    "name": sender.name,
                    "profile_pic": None
                },
                "connected_at": connection.connected_at.isoformat() if connection.connected_at else None
            }
        
        raise Exception("Failed to create connection")
    
    def reject_request(self, request_id: int, receiver_id: int) -> None:
        """Reject a connection request"""
        # Get the request
        request = self.db.query(ConnectionRequest).filter(ConnectionRequest.id == request_id).first()
        if not request:
            raise LookupError("Connection request not found")
        
        # Verify the receiver is correct
        if request.receiver_id != receiver_id:
            raise PermissionError("You cannot reject this request")
        
        # Check if already processed
        if request.status != 'pending':
            raise ValueError(f"Request is already {request.status}")
        
        # Update request status
        request.status = 'rejected'
        self.db.commit()
    
    def remove_connection(self, connection_id: int, user_id: int) -> None:
        """Remove an existing connection"""
        connection = self.db.query(Connection).filter(Connection.connection_id == connection_id).first()
        if not connection:
            raise LookupError("Connection not found")
        
        # Verify user is part of this connection
        if connection.follower_uid != user_id:
            raise PermissionError("You cannot remove this connection")
        
        # Remove bidirectional connection
        other_user_id = connection.followed_uid
        self._remove_bidirectional_connection(user_id, other_user_id)
        invalidate_feed_for_users(self.db, user_id, other_user_id)

    def get_pending_requests(self, user_id: int) -> List[Dict[str, Any]]:
        """Get pending requests received by user"""
        requests = (
            self.db.query(ConnectionRequest)
            .join(User, ConnectionRequest.sender_id == User.uid)
            .filter(
                and_(
                    ConnectionRequest.receiver_id == user_id,
                    ConnectionRequest.status == 'pending'
                )
            )
            .order_by(desc(ConnectionRequest.created_at))
            .all()
        )
        
        return [self._format_received_request(req) for req in requests]
    
    def get_sent_requests(self, user_id: int) -> List[Dict[str, Any]]:
        """Get requests sent by user"""
        requests = (
            self.db.query(ConnectionRequest)
            .join(User, ConnectionRequest.receiver_id == User.uid)
            .filter(
                and_(
                    ConnectionRequest.sender_id == user_id,
                    ConnectionRequest.status == 'pending'
                )
            )
            .order_by(desc(ConnectionRequest.created_at))
            .all()
        )
        
        return [self._format_sent_request(req) for req in requests]
    
    def _are_connected(self, user1_id: int, user2_id: int) -> bool:
        """Check if two users are connected"""
        connection = (
            self.db.query(Connection)
            .filter(
                or_(
                    and_(
                        Connection.follower_uid == user1_id,
                        Connection.followed_uid == user2_id
                    ),
                    and_(
                        Connection.follower_uid == user2_id,
                        Connection.followed_uid == user1_id
                    )
                )
            )
            .first()
        )
        return connection is not None
    
    def _create_bidirectional_connection(self, user1_id: int, user2_id: int) -> None:
        """Create connections in both directions"""
        # Create connection 1 -> 2
        conn1 = Connection(follower_uid=user1_id, followed_uid=user2_id)
        self.db.add(conn1)
        
        # Create connection 2 -> 1
        conn2 = Connection(follower_uid=user2_id, followed_uid=user1_id)
        self.db.add(conn2)
        
        self.db.commit()
    
    def _remove_bidirectional_connection(self, user1_id: int, user2_id: int) -> None:
        """Remove connections in both directions"""
        self.db.query(Connection).filter(
            or_(
                and_(
                    Connection.follower_uid == user1_id,
                    Connection.followed_uid == user2_id
                ),
                and_(
                    Connection.follower_uid == user2_id,
                    Connection.followed_uid == user1_id
                )
            )
        ).delete()
        self.db.commit()
    
    def _format_request(self, request: ConnectionRequest, sender: User = None, receiver: User = None) -> Dict[str, Any]:
        """Format request for response"""
        result = {
            "id": request.id,
            "sender_id": request.sender_id,
            "receiver_id": request.receiver_id,
            "status": request.status,
            "message": request.message,
            "created_at": request.created_at.isoformat() if request.created_at else None,
            "updated_at": request.updated_at.isoformat() if request.updated_at else None
        }
        
        if sender:
            result["sender"] = {
                "id": sender.uid,
                "username": sender.username,
                "name": sender.name,
                "profile_pic": None
            }
        
        if receiver:
            result["receiver"] = {
                "id": receiver.uid,
                "username": receiver.username,
                "name": receiver.name,
                "profile_pic": None
            }
        
        return result
    
    def _format_received_request(self, request: ConnectionRequest) -> Dict[str, Any]:
        """Format received request with sender info"""
        sender = request.sender
        return {
            "id": request.id,
            "sender_id": request.sender_id,
            "receiver_id": request.receiver_id,
            "status": request.status,
            "message": request.message,
            "sender": {
                "id": sender.uid,
                "username": sender.username,
                "name": sender.name,
                "profile_pic": None
            },
            "created_at": request.created_at.isoformat() if request.created_at else None,
            "updated_at": request.updated_at.isoformat() if request.updated_at else None
        }
    
    def _format_sent_request(self, request: ConnectionRequest) -> Dict[str, Any]:
        """Format sent request with receiver info"""
        receiver = request.receiver
        return {
            "id": request.id,
            "sender_id": request.sender_id,
            "receiver_id": request.receiver_id,
            "status": request.status,
            "message": request.message,
            "receiver": {
                "id": receiver.uid,
                "username": receiver.username,
                "name": receiver.name,
                "profile_pic": None
            },
            "created_at": request.created_at.isoformat() if request.created_at else None,
            "updated_at": request.updated_at.isoformat() if request.updated_at else None
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
