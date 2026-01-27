"""
Auto-ticket creation rule model
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class TriggerType(str, Enum):
    """Trigger type for auto-ticket creation"""

    KEYWORD = "keyword"
    CATEGORY = "category"
    UNRESPONDED = "unresponded"
    TIME_BASED = "time_based"


class AutoTicketRuleStatus(str, Enum):
    """Auto-ticket rule status"""

    ACTIVE = "active"
    INACTIVE = "inactive"


class AutoTicketRule(Base):
    """
    Auto-ticket creation rule model

    Automatically creates tickets based on incoming messages or conditions

    Attributes:
        id: Primary key (UUID)
        hotel_id: Foreign key to hotel
        name: Rule name
        trigger_type: Type of trigger
        keywords: Keywords to match (JSON array)
        ticket_category: Default ticket category
        ticket_priority: Default ticket priority
        ticket_title_template: Title template for created tickets
        ticket_description_template: Description template
        auto_assign: Whether to auto-assign the ticket
        priority_level: Rule priority (higher = more priority)
        is_active: Active status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "auto_ticket_rules"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    hotel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hotels.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger_type: Mapped[str] = mapped_column(
        String(20), default=TriggerType.KEYWORD.value
    )
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    ticket_category: Mapped[str] = mapped_column(String(20), default="other")
    ticket_priority: Mapped[str] = mapped_column(String(10), default="P3")
    ticket_title_template: Mapped[str] = mapped_column(
        String(200), default="Auto-created ticket"
    )
    ticket_description_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    auto_assign: Mapped[bool] = mapped_column(default=False)
    priority_level: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel")  # type: ignore

    def __repr__(self) -> str:
        return f"<AutoTicketRule(id={self.id}, name={self.name}, type={self.trigger_type})>"
