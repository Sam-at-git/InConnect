"""
CRUD operations for Conversation model
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    """CRUD operations for Conversation"""

    async def get_by_guest_and_hotel(
        self,
        db: AsyncSession,
        hotel_id: str,
        guest_id: str,
    ) -> Conversation | None:
        """
        Get conversation by guest and hotel

        Args:
            db: Database session
            hotel_id: Hotel ID
            guest_id: Guest ID

        Returns:
            Conversation or None
        """
        result = await db.execute(
            select(Conversation)
            .filter(
                Conversation.hotel_id == hotel_id,
                Conversation.guest_id == guest_id,
                Conversation.status == "active",
            )
            .order_by(Conversation.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def get_by_hotel(
        self,
        db: AsyncSession,
        hotel_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Conversation]:
        """
        Get conversations by hotel ID

        Args:
            db: Database session
            hotel_id: Hotel ID
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of conversations
        """
        result = await db.execute(
            select(Conversation)
            .filter(Conversation.hotel_id == hotel_id)
            .order_by(Conversation.last_message_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> Conversation | None:
        """
        Get conversation with messages

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            Conversation with messages or None
        """
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .filter(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_active(
        self,
        db: AsyncSession,
        hotel_id: str | None = None,
        limit: int = 100,
    ) -> list[Conversation]:
        """
        Get active conversations

        Args:
            db: Database session
            hotel_id: Filter by hotel ID
            limit: Maximum records to return

        Returns:
            List of active conversations
        """
        query = select(Conversation).filter(Conversation.status == "active")

        if hotel_id:
            query = query.filter(Conversation.hotel_id == hotel_id)

        result = await db.execute(
            query.order_by(Conversation.last_message_at.desc()).limit(limit)
        )
        return list(result.scalars().all())


# Create singleton instance
conversation = CRUDConversation(Conversation)
