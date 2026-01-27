"""
Routing Rule ORM model
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


class RoutingRuleType(str, Enum):
    """Routing rule type enum"""

    KEYWORD = "keyword"  # Match by keyword
    CATEGORY = "category"  # Match by ticket category
    PRIORITY = "priority"  # Match by priority
    ROUND_ROBIN = "round_robin"  # Distribute evenly
    MANUAL = "manual"  # Manual assignment


class RoutingRuleStatus(str, Enum):
    """Routing rule status enum"""

    ACTIVE = "active"
    INACTIVE = "inactive"


class RoutingRule(Base):
    """
    Message routing rule model

    Attributes:
        id: Primary key (UUID)
        hotel_id: Foreign key to hotel
        name: Rule name
        rule_type: Rule type
        keywords: Keywords for matching (JSON array)
        category: Category to match
        priority: Priority to match
        target_staff_ids: Target staff IDs for assignment (JSON array)
        priority_level: Rule priority (higher = more priority)
        is_active: Active status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "routing_rules"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    hotel_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hotels.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_type: Mapped[str] = mapped_column(
        String(20), default=RoutingRuleType.KEYWORD.value
    )
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(10), nullable=True)
    target_staff_ids: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    priority_level: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="routing_rules")

    def __repr__(self) -> str:
        return f"<RoutingRule(id={self.id}, name={self.name}, type={self.rule_type})>"
