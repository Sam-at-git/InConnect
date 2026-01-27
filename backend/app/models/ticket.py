"""
Ticket ORM model
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.staff import Staff
    from app.models.conversation import Conversation
    from app.models.ticket_timeline import TicketTimeline


class TicketStatus(str, Enum):
    """Ticket status enum"""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class TicketPriority(str, Enum):
    """Ticket priority enum"""

    P1 = "P1"  # Critical
    P2 = "P2"  # High
    P3 = "P3"  # Medium
    P4 = "P4"  # Low


class TicketCategory(str, Enum):
    """Ticket category enum"""

    MAINTENANCE = "maintenance"
    HOUSEKEEPING = "housekeeping"
    SERVICE = "service"
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    OTHER = "other"


class Ticket(Base):
    """
    Support ticket model

    Attributes:
        id: Primary key (UUID with prefix)
        hotel_id: Foreign key to hotel
        conversation_id: Foreign key to conversation
        assigned_to: Foreign key to staff (assignee)
        title: Ticket title
        description: Detailed description
        category: Ticket category
        priority: Ticket priority
        status: Ticket status
        due_at: Due date for resolution
        resolved_at: Resolution timestamp
        closed_at: Closing timestamp
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"TK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
    )
    hotel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hotels.id"), nullable=False, index=True
    )
    conversation_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    assigned_to: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("staff.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        String(20), default=TicketCategory.OTHER.value
    )
    priority: Mapped[str] = mapped_column(
        String(10), default=TicketPriority.P3.value
    )
    status: Mapped[str] = mapped_column(
        String(20), default=TicketStatus.PENDING.value, index=True
    )

    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="tickets")
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="tickets")
    assignee: Mapped["Staff"] = relationship(
        "Staff", foreign_keys=[assigned_to], back_populates="assigned_tickets"
    )
    timelines: Mapped[list["TicketTimeline"]] = relationship(
        "TicketTimeline", back_populates="ticket", cascade="all, delete-orphan"
    )

    @property
    def is_overdue(self) -> bool:
        """Check if ticket is overdue"""
        if self.due_at is None:
            return False
        return self.due_at < datetime.utcnow() and self.status not in (
            TicketStatus.RESOLVED.value,
            TicketStatus.CLOSED.value,
        )

    def __repr__(self) -> str:
        return f"<Ticket(id={self.id}, title={self.title}, status={self.status})>"
