"""
CRUD operations for Message model
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.message import Message
from app.schemas.message import MessageCreate


class CRUDMessage(CRUDBase[Message, MessageCreate, dict]):
    """CRUD operations for Message"""

    async def get_by_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
        limit: int = 100,
    ) -> list[Message]:
        """
        Get messages by conversation ID

        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Maximum records to return

        Returns:
            List of messages
        """
        result = await db.execute(
            select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.sent_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_wechat_msg_id(
        self,
        db: AsyncSession,
        wechat_msg_id: str,
    ) -> Message | None:
        """
        Get message by WeChat message ID (for deduplication)

        Args:
            db: Database session
            wechat_msg_id: WeChat message ID

        Returns:
            Message or None
        """
        result = await db.execute(
            select(Message).filter(Message.wechat_msg_id == wechat_msg_id)
        )
        return result.scalar_one_or_none()

    async def create_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        message_type: str,
        direction: str,
        content: str | None = None,
        media_url: str | None = None,
        sender_id: str | None = None,
        wechat_msg_id: str | None = None,
    ) -> Message:
        """
        Create a new message

        Args:
            db: Database session
            conversation_id: Conversation ID
            message_type: Message type
            direction: Message direction
            content: Message content
            media_url: Media URL
            sender_id: Sender ID
            wechat_msg_id: WeChat message ID

        Returns:
            Created message
        """
        message_data = {
            "conversation_id": conversation_id,
            "message_type": message_type,
            "direction": direction,
            "content": content,
            "media_url": media_url,
            "sender_id": sender_id,
            "wechat_msg_id": wechat_msg_id,
        }

        message = Message(**message_data)
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message


# Create singleton instance
message = CRUDMessage(Message)
