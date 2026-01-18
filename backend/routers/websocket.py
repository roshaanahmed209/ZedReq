"""WebSocket Router - Real-time notifications"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from websocket.manager import connection_manager
from services.auth_service import AuthService
from config.database import get_database

router = APIRouter()


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time notifications.
    Connect with: ws://host/ws/notifications?token=<jwt_token>
    """
    # Validate token and get user
    try:
        db = get_database()
        auth_service = AuthService(db)
        user = auth_service.verify_token(token)
        user_id = user["id"]  # Now an int
    except Exception as e:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return
    
    # Accept connection and register with manager
    await connection_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive, handle incoming messages
            data = await websocket.receive_text()
            
            # Handle ping/pong for keepalive
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id)
    except Exception as e:
        connection_manager.disconnect(user_id)
        print(f"WebSocket error for user {user_id}: {e}")
