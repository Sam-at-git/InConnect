"""
SLA Configuration ORM model
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class SLAConfig(Base):
    """
    SLA (Service Level Agreement) Configuration model

    Defines response and resolution time targets for different priority levels.

    Attributes:
        id: Primary key (UUID)
        hotel_id: Foreign key to hotel (for multi-tenant support)
        priority: Ticket priority level (P1-P4)
        response_minutes: Target response time in minutes
        resolution_minutes: Target resolution time in minutes
        is_active: Whether this configuration is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "sla_configs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    hotel_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("hotels.id", ondelete="CASCADE"), nullable=True, index=True
    )
    priority: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    response_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    resolution_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=240)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="sla_configs")

    def __repr__(self) -> str:
        return f"<SLAConfig(id={self.id}, priority={self.priority}, response={self.response_minutes}m)>"
