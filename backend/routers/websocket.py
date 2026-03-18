"""WebSocket Router - Real-time notifications using ORM"""
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from websocket.manager import connection_manager
from services.auth_service import AuthService
from config.database_orm import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.
    Connect to ws://host/ws/notifications, then send first message: {"type": "auth", "token": "<jwt>"}.
    """
    await websocket.accept()
    user_id = None
    try:
        # Require first message to be auth with token (no token in URL)
        first_msg = await websocket.receive_text()
        try:
            data = json.loads(first_msg)
            if data.get("type") != "auth":
                raise ValueError("First message must be {\"type\": \"auth\", \"token\": \"<jwt>\"}")
            token = data.get("token") or ""
            if not token:
                raise ValueError("Token required in auth message")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("WebSocket auth message invalid: %s", e)
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
            logger.debug("WebSocket authentication failed: %s", auth_error)
            await websocket.send_json({"type": "error", "message": "Invalid or expired token"})
            await websocket.close(code=4001, reason="Invalid authentication token")
            return
        finally:
            db.close()

        await connection_manager.connect(websocket, user_id)
        logger.info("WebSocket connected: User %s", user_id)
        await websocket.send_json({"type": "connected", "message": "WebSocket connection established"})

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        if user_id is not None:
            connection_manager.disconnect(user_id, websocket)
        logger.info("WebSocket disconnected for user %s", user_id)
    except Exception as e:
        logger.error("WebSocket error for user %s: %s", user_id, e)
        if user_id is not None:
            connection_manager.disconnect(user_id, websocket)
