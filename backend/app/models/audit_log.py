"""
Audit Log ORM model
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.staff import Staff


class AuditAction(str, Enum):
    """Audit action types"""

    # Ticket actions
    TICKET_CREATE = "ticket_create"
    TICKET_UPDATE = "ticket_update"
    TICKET_DELETE = "ticket_delete"
    TICKET_ASSIGN = "ticket_assign"
    TICKET_STATUS_CHANGE = "ticket_status_change"

    # Message actions
    MESSAGE_SEND = "message_send"
    MESSAGE_VIEW = "message_view"

    # Staff actions
    STAFF_CREATE = "staff_create"
    STAFF_UPDATE = "staff_update"
    STAFF_DELETE = "staff_delete"

    # Rule actions
    RULE_CREATE = "rule_create"
    RULE_UPDATE = "rule_update"
    RULE_DELETE = "rule_delete"

    # Settings actions
    SETTINGS_UPDATE = "settings_update"

    # Auth actions
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"

    # Export actions
    DATA_EXPORT = "data_export"


class AuditLog(Base):
    """
    Audit log model for tracking all system actions

    Attributes:
        id: Primary key (UUID)
        hotel_id: Foreign key to hotel
        staff_id: Foreign key to staff (actor)
        action: Action type
        resource_type: Type of resource affected
        resource_id: ID of resource affected
        old_value: Old value (for updates)
        new_value: New value
        ip_address: Client IP address
        user_agent: Client user agent
        created_at: Timestamp of action
    """

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    hotel_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    staff_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("staff.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog(action={self.action}, resource={self.resource_type})>"
