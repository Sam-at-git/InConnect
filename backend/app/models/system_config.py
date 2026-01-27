"""
System Configuration ORM model
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    pass


class SystemConfig(Base):
    """
    System configuration model for storing key-value settings

    Attributes:
        id: Primary key (UUID)
        key: Configuration key (unique)
        value: Configuration value (JSON)
        description: Configuration description
        category: Configuration category for grouping
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "system_configs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="general", index=True)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<SystemConfig(key={self.key}, category={self.category})>"
