"""
Ticket Timeline ORM model
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.ticket import Ticket
    from app.models.staff import Staff


class TimelineEventType(str, Enum):
    """Timeline event type enum"""

    CREATED = "created"
    ASSIGNED = "assigned"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    COMMENT = "comment"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
    # SLA related events
    SLA_APPLIED = "sla_applied"
    SLA_WARNING = "sla_warning"
    SLA_BREACHED = "sla_breached"
    SLA_ESCALATED = "sla_escalated"


class TicketTimeline(Base):
    """
    Ticket change history model

    Attributes:
        id: Primary key (UUID)
        ticket_id: Foreign key to ticket
        staff_id: Foreign key to staff (who made the change)
        event_type: Event type
        old_value: Old value before change
        new_value: New value after change
        comment: Additional comment
        created_at: Creation timestamp
    """

    __tablename__ = "ticket_timeline"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    ticket_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    staff_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("staff.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="timelines")
    staff: Mapped["Staff"] = relationship("Staff", back_populates="ticket_timelines")

    def __repr__(self) -> str:
        return f"<TicketTimeline(id={self.id}, event_type={self.event_type}, ticket_id={self.ticket_id})>"
