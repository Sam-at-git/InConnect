"""
Staff ORM model
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
    from app.models.ticket import Ticket
    from app.models.ticket_timeline import TicketTimeline


class StaffRole(str, Enum):
    """Staff role enum"""

    ADMIN = "admin"
    MANAGER = "manager"
    RECEPTIONIST = "receptionist"
    HOUSEKEEPING = "housekeeping"
    MAINTENANCE = "maintenance"
    OTHER = "other"


class StaffStatus(str, Enum):
    """Staff status enum"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


class Staff(Base):
    """
    Staff member model

    Attributes:
        id: Primary key (UUID)
        hotel_id: Foreign key to hotel
        name: Staff name
        wechat_userid: WeChat user ID
        phone: Contact phone number
        email: Email address
        role: Staff role
        department: Department name
        status: Staff status
        is_available: Availability flag for ticket assignment
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "staff"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    hotel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hotels.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    wechat_userid: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default=StaffRole.OTHER.value)
    department: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=StaffStatus.ACTIVE.value)
    is_available: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    hotel: Mapped["Hotel"] = relationship(
        "Hotel", back_populates="staff_members"
    )
    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", foreign_keys="[Ticket.assigned_to]", back_populates="assignee"
    )
    ticket_timelines: Mapped[list["TicketTimeline"]] = relationship(
        "TicketTimeline", back_populates="staff"
    )

    def __repr__(self) -> str:
        return f"<Staff(id={self.id}, name={self.name}, role={self.role})>"
