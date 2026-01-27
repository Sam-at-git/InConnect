"""
WebSocket notification manager
"""

import json
from typing import Any, Callable,Awaitable

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger("app.services.websocket")


class WebSocketMessage(BaseModel):
    """WebSocket message format"""

    type: str  # notification, ticket_update, new_message, etc.
    data: dict[str, Any]


class ConnectionManager:
    """
    WebSocket connection manager for real-time notifications
    """

    def __init__(self) -> None:
        # Map user_id to WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """
        Connect a WebSocket client

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user: {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """
        Disconnect a WebSocket client

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user: {user_id}")

    async def send_to_user(
        self,
        user_id: str,
        message: WebSocketMessage,
    ) -> None:
        """
        Send message to specific user

        Args:
            user_id: User ID
            message: Message to send
        """
        if user_id not in self.active_connections:
            return

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message.model_dump())
            except Exception as e:
                logger.error(
                    f"Failed to send WebSocket message to user {user_id}",
                    exc_info=True,
                )
                # Remove dead connection
                self.disconnect(connection, user_id)

    async def broadcast(self, message: WebSocketMessage) -> None:
        """
        Broadcast message to all connected users

        Args:
            message: Message to broadcast
        """
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message.model_dump())
                except Exception:
                    self.disconnect(connection, user_id)

    async def send_ticket_notification(
        self,
        user_id: str,
        ticket_id: str,
        ticket_title: str,
        notification_type: str,  # assigned, updated, commented
    ) -> None:
        """
        Send ticket-related notification

        Args:
            user_id: User ID to notify
            ticket_id: Ticket ID
            ticket_title: Ticket title
            notification_type: Type of notification
        """
        type_messages = {
            "assigned": f"您收到了新工单: {ticket_title}",
            "updated": f"工单已更新: {ticket_title}",
            "commented": f"工单有新评论: {ticket_title}",
        }

        message = WebSocketMessage(
            type="ticket_notification",
            data={
                "ticket_id": ticket_id,
                "ticket_title": ticket_title,
                "notification_type": notification_type,
                "message": type_messages.get(notification_type, "工单通知"),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        await self.send_to_user(user_id, message)

    async def send_new_message_notification(
        self,
        user_id: str,
        conversation_id: str,
        guest_name: str,
        message_preview: str,
    ) -> None:
        """
        Send new message notification

        Args:
            user_id: User ID to notify
            conversation_id: Conversation ID
            guest_name: Guest name
            message_preview: Message content preview
        """
        message = WebSocketMessage(
            type="new_message",
            data={
                "conversation_id": conversation_id,
                "guest_name": guest_name,
                "message_preview": message_preview[:100],
                "message": f"来自 {guest_name} 的新消息",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        await self.send_to_user(user_id, message)


# Create singleton instance
manager = ConnectionManager()

# Import at end to avoid circular dependency
from datetime import datetime
