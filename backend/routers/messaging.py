"""Messaging Router - WebSocket and HTTP endpoints for messaging"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
import logging
import json

from websocket.manager import connection_manager
from services.auth_service import AuthService
from services.messaging_service import MessagingService
from services.network_service import NetworkService
from dependencies.auth import get_current_user
from config.database_orm import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/messages")
async def websocket_messages(websocket: WebSocket):
    """
    WebSocket endpoint for real-time messaging.
    Connect to ws://host/api/messaging/messages, then send first message: {"type": "auth", "token": "<jwt>"}.
    """
    await websocket.accept()
    user_id = None
    try:
        first_msg = await websocket.receive_text()
        try:
            message_data = json.loads(first_msg)
            if message_data.get("type") != "auth":
                raise ValueError("First message must be {\"type\": \"auth\", \"token\": \"<jwt>\"}")
            token = message_data.get("token") or ""
            if not token:
                raise ValueError("Token required in auth message")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("WebSocket messaging auth message invalid: %s", e)
            await websocket.send_json({"type": "error", "message": "Invalid or missing auth message"})
            await websocket.close(code=4001, reason="Invalid authentication")
            return

        db = next(get_db())
        try:
            auth_service = AuthService(db)
            user = auth_service.verify_token(token)
            user_id = user.get("id") or user.get("uid")
            if not user_id:
                raise ValueError("User ID not found in token")
            user_id = int(user_id)
        except Exception as auth_error:
            logger.debug("WebSocket messaging authentication failed: %s", auth_error)
            await websocket.send_json({"type": "error", "message": "Invalid or expired token"})
            await websocket.close(code=4001, reason="Invalid authentication token")
            return
        finally:
            db.close()

        await connection_manager.connect(websocket, user_id)
        logger.info("WebSocket messaging connected: User %s", user_id)
        
        # Initialize messaging service
        messaging_service = MessagingService()
        
        # Get connected user IDs for validation (load once at connection start)
        db_session = next(get_db())
        try:
            network_service = NetworkService(db_session)
            connected_users = network_service.get_user_connections(user_id)
            connected_user_ids = {user["id"] for user in connected_users}
        finally:
            db_session.close()
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Messaging WebSocket connection established",
            "user_id": user_id
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type")
                
                # Handle ping/pong for keepalive
                if message_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
                # Handle sending a message
                elif message_type == "send_message":
                    recipient_id = message_data.get("recipient_id")
                    content = message_data.get("content")
                    msg_type = message_data.get("message_type", "text")
                    
                    if not recipient_id or not content:
                        await websocket.send_json({
                            "type": "error",
                            "message": "recipient_id and content are required"
                        })
                        continue
                    
                    recipient_id = int(recipient_id)
                    
                    # Check if users are connected
                    if recipient_id not in connected_user_ids:
                        await websocket.send_json({
                            "type": "error",
                            "message": "You can only message users you are connected with"
                        })
                        continue
                    
                    # Send message via messaging service
                    sent_message = await messaging_service.send_message(
                        sender_id=user_id,
                        recipient_id=recipient_id,
                        content=content,
                        message_type=msg_type
                    )
                    
                    if sent_message:
                        # Send confirmation to sender
                        await websocket.send_json({
                            "type": "message_sent",
                            "message": sent_message
                        })
                        
                        # Send message to recipient if online
                        await connection_manager.send_to_user(
                            int(recipient_id),
                            {
                                "type": "new_message",
                                "message": sent_message
                            }
                        )
                    else:
                        logger.error(f"Failed to send message from {user_id} to {recipient_id}: messaging_service.send_message returned None")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to send message. Please check Firebase configuration or try again later."
                        })
                
                # Handle getting messages
                elif message_type == "get_messages":
                    recipient_id = message_data.get("recipient_id")
                    limit = message_data.get("limit", 50)
                    
                    if not recipient_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "recipient_id is required"
                        })
                        continue
                    
                    recipient_id = int(recipient_id)
                    
                    # Check if users are connected
                    if recipient_id not in connected_user_ids:
                        await websocket.send_json({
                            "type": "error",
                            "message": "You can only view messages with users you are connected with"
                        })
                        continue
                    
                    messages = await messaging_service.get_messages(
                        user1_id=user_id,
                        user2_id=recipient_id,
                        limit=limit
                    )
                    
                    await websocket.send_json({
                        "type": "messages",
                        "recipient_id": recipient_id,
                        "messages": messages
                    })
                
                # Handle marking messages as read
                elif message_type == "mark_read":
                    recipient_id = message_data.get("recipient_id")
                    message_id = message_data.get("message_id")
                    
                    if not recipient_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "recipient_id is required"
                        })
                        continue
                    
                    if message_id:
                        success = await messaging_service.mark_message_as_read(
                            user1_id=user_id,
                            user2_id=int(recipient_id),
                            message_id=message_id
                        )
                    else:
                        success = await messaging_service.mark_conversation_as_read(
                            user1_id=user_id,
                            user2_id=int(recipient_id)
                        )
                    
                    await websocket.send_json({
                        "type": "read_status",
                        "success": success
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling message: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing request: {str(e)}"
                })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket messaging disconnected normally for user {user_id}")
        if user_id:
            connection_manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket messaging error for user {user_id}: {e}", exc_info=True)
        if user_id:
            connection_manager.disconnect(user_id, websocket)


class SendMessageRequest(BaseModel):
    """Send message request body"""
    recipient_id: int = Field(..., gt=0)
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = Field(default="text")


@router.get("/conversations")
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user (only with connected users)"""
    try:
        # Get user's connected users with full info
        network_service = NetworkService(db)
        connected_users = network_service.get_user_connections(current_user["id"])
        connected_user_ids = [user["id"] for user in connected_users]
        
        # Create a map of user_id -> user_info for quick lookup
        connected_users_map = {user["id"]: user for user in connected_users}
        
        # Get conversations filtered by connections
        messaging_service = MessagingService()
        conversations = await messaging_service.get_conversations(
            current_user["id"],
            connected_user_ids=connected_user_ids
        )
        
        # Enrich conversations with user information
        enriched_conversations = []
        for conv in conversations:
            other_user_id = conv["other_user_id"]
            user_info = connected_users_map.get(other_user_id)
            
            enriched_conv = {
                **conv,
                "other_user": user_info if user_info else {
                    "id": other_user_id,
                    "name": f"User {other_user_id}",
                    "username": f"user_{other_user_id}",
                    "profile_pic": None
                }
            }
            enriched_conversations.append(enriched_conv)
        
        return {
            "success": True,
            "conversations": enriched_conversations
        }
    except Exception as e:
        logger.error(f"Error getting conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get("/messages/{recipient_id}")
async def get_messages(
    recipient_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get messages for a conversation with a specific user"""
    try:
        messaging_service = MessagingService()
        messages = await messaging_service.get_messages(
            user1_id=current_user["id"],
            user2_id=recipient_id,
            limit=limit
        )
        return {
            "success": True,
            "recipient_id": recipient_id,
            "messages": messages
        }
    except Exception as e:
        logger.error(f"Error getting messages: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )


@router.post("/messages", status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to another user (only if connected)"""
    try:
        # Check if users are connected
        network_service = NetworkService(db)
        connected_users = network_service.get_user_connections(current_user["id"])
        connected_user_ids = [user["id"] for user in connected_users]
        
        if message_data.recipient_id not in connected_user_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only message users you are connected with"
            )
        
        messaging_service = MessagingService()
        sent_message = await messaging_service.send_message(
            sender_id=current_user["id"],
            recipient_id=message_data.recipient_id,
            content=message_data.content,
            message_type=message_data.message_type
        )
        
        if not sent_message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message"
            )
        
        # Notify recipient if online
        await connection_manager.send_to_user(
            message_data.recipient_id,
            {
                "type": "new_message",
                "message": sent_message
            }
        )
        
        return {
            "success": True,
            "message": sent_message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.post("/messages/{recipient_id}/read")
async def mark_conversation_read(
    recipient_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Mark all messages in a conversation as read"""
    try:
        messaging_service = MessagingService()
        success = await messaging_service.mark_conversation_as_read(
            user1_id=current_user["id"],
            user2_id=recipient_id
        )
        
        return {
            "success": success
        }
    except Exception as e:
        logger.error(f"Error marking conversation as read: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark conversation as read"
        )
