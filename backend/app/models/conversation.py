"""
Conversation ORM model
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.message import Message
    from app.models.ticket import Ticket


class ConversationStatus(str, Enum):
    """Conversation status enum"""

    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class Conversation(Base):
    """
    Guest conversation model

    Attributes:
        id: Primary key (UUID)
        hotel_id: Foreign key to hotel
        guest_id: External guest ID from WeChat
        guest_name: Guest name
        guest_phone: Guest phone number
        guest_avatar: Guest avatar URL
        status: Conversation status
        last_message_at: Last message timestamp
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    hotel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hotels.id"), nullable=False, index=True
    )
    guest_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    guest_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    guest_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    guest_avatar: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default=ConversationStatus.ACTIVE.value
    )

    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    hotel: Mapped["Hotel"] = relationship(
        "Hotel", back_populates="conversations"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="conversation"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, guest_id={self.guest_id}, status={self.status})>"
