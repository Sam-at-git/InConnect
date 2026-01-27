"""
Message ORM model
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class MessageType(str, Enum):
    """Message type enum"""

    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    FILE = "file"
    LOCATION = "location"
    LINK = "link"
    EVENT = "event"


class MessageDirection(str, Enum):
    """Message direction enum"""

    INBOUND = "inbound"  # From guest to hotel
    OUTBOUND = "outbound"  # From hotel to guest


class Message(Base):
    """
    Message model

    Attributes:
        id: Primary key (UUID)
        conversation_id: Foreign key to conversation
        message_type: Message type
        direction: Message direction (inbound/outbound)
        content: Message content
        media_url: Media URL for non-text messages
        sender_id: Sender ID (WeChat user ID or staff ID)
        wechat_msg_id: WeChat message ID for deduplication
        is_read: Read status
        sent_at: Message send timestamp
        created_at: Creation timestamp
    """

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    message_type: Mapped[str] = mapped_column(
        String(20), default=MessageType.TEXT.value
    )
    direction: Mapped[str] = mapped_column(
        String(20), default=MessageDirection.INBOUND.value
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    sender_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    wechat_msg_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False)

    sent_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, type={self.message_type}, direction={self.direction})>"
