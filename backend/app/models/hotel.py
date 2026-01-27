"""
Hotel ORM model
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.staff import Staff
    from app.models.conversation import Conversation
    from app.models.ticket import Ticket
    from app.models.routing_rule import RoutingRule
    from app.models.sla_config import SLAConfig


class Hotel(Base):
    """
    Hotel information model

    Attributes:
        id: Primary key (UUID)
        name: Hotel name
        corp_id: WeChat corporate ID
        address: Hotel address
        contact_phone: Contact phone number
        contact_person: Contact person name
        status: Hotel status (active/inactive)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "hotels"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    corp_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    staff_members: Mapped[list["Staff"]] = relationship(
        "Staff", back_populates="hotel", cascade="all, delete-orphan"
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="hotel", cascade="all, delete-orphan"
    )
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="hotel", cascade="all, delete-orphan"
    )
    routing_rules: Mapped[list["RoutingRule"]] = relationship(
        "RoutingRule", back_populates="hotel", cascade="all, delete-orphan"
    )
    sla_configs: Mapped[list["SLAConfig"]] = relationship(
        "SLAConfig", back_populates="hotel", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Hotel(id={self.id}, name={self.name}, corp_id={self.corp_id})>"
