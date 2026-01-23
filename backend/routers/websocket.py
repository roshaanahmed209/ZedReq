"""WebSocket Router - Real-time notifications using ORM"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
import logging

from websocket.manager import connection_manager
from services.auth_service import AuthService
from config.database_orm import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time notifications.
    Connect with: ws://host/ws/notifications?token=<jwt_token>
    """
    # Validate token and get user BEFORE accepting connection
    user_id = None
    try:
        # Create a new session for this WebSocket connection
        db = next(get_db())
        try:
            auth_service = AuthService(db)
            user = auth_service.verify_token(token)
            user_id = user.get("id") or user.get("uid")  # Support both id and uid
            if not user_id:
                raise ValueError("User ID not found in token")
            user_id = int(user_id)  # Ensure it's an integer
            logger.info(f"WebSocket authentication successful for user {user_id}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        # Accept connection first, then close with error
        await websocket.accept()
        await websocket.close(code=4001, reason="Invalid authentication token")
        return
    
    # Accept connection and register with manager
    try:
        await connection_manager.connect(websocket, user_id)
        logger.info(f"WebSocket connected: User {user_id}")
        
        # Send welcome message
        await websocket.send_json({"type": "connected", "message": "WebSocket connection established"})
        
        while True:
            # Keep connection alive, handle incoming messages
            data = await websocket.receive_text()
            
            # Handle ping/pong for keepalive
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally for user {user_id}")
        connection_manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        connection_manager.disconnect(user_id, websocket)
