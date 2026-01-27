"""
WebSocket endpoint for real-time notifications
"""

import json
from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from jose import JWTError

from app.services.websocket_manager import manager, WebSocketMessage
from app.core.security import decode_access_token
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("app.api.v1.websocket")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Annotated[str, Query(...)],
) -> None:
    """
    WebSocket endpoint for real-time notifications

    Args:
        websocket: WebSocket connection
        token: JWT access token
    """
    # Verify token
    try:
        payload = decode_access_token(token)
        if payload is None:
            await websocket.close(code=1008, reason="Invalid token")
            return

        user_id: str = payload.get("sub")
        if user_id is None:
            await websocket.close(code=1008, reason="Invalid token payload")
            return
    except JWTError:
        await websocket.close(code=1008, reason="Token verification failed")
        return

    # Connect WebSocket
    await manager.connect(websocket, user_id)

    try:
        # Send connected confirmation
        await websocket.send_json({
            "type": "connected",
            "data": {
                "message": "WebSocket connected successfully",
                "user_id": user_id,
            },
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle client messages (ping, subscribe, etc.)
            if message_data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "data": {"timestamp": message_data.get("timestamp")},
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(
            f"WebSocket error for user {user_id}",
            exc_info=True,
        )
        manager.disconnect(websocket, user_id)
