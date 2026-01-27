"""
Permission and Role ORM models
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.hotel import Hotel
    from app.models.staff import Staff


class PermissionType(str, Enum):
    """Permission type enum"""

    # Ticket permissions
    TICKET_VIEW = "ticket_view"
    TICKET_CREATE = "ticket_create"
    TICKET_EDIT = "ticket_edit"
    TICKET_DELETE = "ticket_delete"
    TICKET_ASSIGN = "ticket_assign"
    TICKET_EXPORT = "ticket_export"

    # Message permissions
    MESSAGE_VIEW = "message_view"
    MESSAGE_SEND = "message_send"
    MESSAGE_EXPORT = "message_export"

    # Report permissions
    REPORT_VIEW = "report_view"
    REPORT_EXPORT = "report_export"

    # Rule permissions
    RULE_VIEW = "rule_view"
    RULE_EDIT = "rule_edit"
    RULE_DELETE = "rule_delete"
    RULE_TEST = "rule_test"

    # Settings permissions
    SETTINGS_VIEW = "settings_view"
    SETTINGS_EDIT = "settings_edit"

    # Staff permissions
    STAFF_VIEW = "staff_view"
    STAFF_CREATE = "staff_create"
    STAFF_EDIT = "staff_edit"
    STAFF_DELETE = "staff_delete"

    # Admin permissions
    ADMIN_ALL = "admin_all"


class SystemRole(str, Enum):
    """System role enum"""

    SUPER_ADMIN = "super_admin"
    HOTEL_ADMIN = "hotel_admin"
    DEPT_MANAGER = "dept_manager"
    STAFF = "staff"
    READ_ONLY = "read_only"


# Role permission mappings
ROLE_PERMISSIONS: dict[SystemRole, list[PermissionType]] = {
    SystemRole.SUPER_ADMIN: [
        PermissionType.ADMIN_ALL,
    ],
    SystemRole.HOTEL_ADMIN: [
        PermissionType.TICKET_VIEW,
        PermissionType.TICKET_CREATE,
        PermissionType.TICKET_EDIT,
        PermissionType.TICKET_DELETE,
        PermissionType.TICKET_ASSIGN,
        PermissionType.TICKET_EXPORT,
        PermissionType.MESSAGE_VIEW,
        PermissionType.MESSAGE_SEND,
        PermissionType.MESSAGE_EXPORT,
        PermissionType.REPORT_VIEW,
        PermissionType.REPORT_EXPORT,
        PermissionType.RULE_VIEW,
        PermissionType.RULE_EDIT,
        PermissionType.RULE_DELETE,
        PermissionType.RULE_TEST,
        PermissionType.SETTINGS_VIEW,
        PermissionType.SETTINGS_EDIT,
        PermissionType.STAFF_VIEW,
        PermissionType.STAFF_CREATE,
        PermissionType.STAFF_EDIT,
        PermissionType.STAFF_DELETE,
    ],
    SystemRole.DEPT_MANAGER: [
        PermissionType.TICKET_VIEW,
        PermissionType.TICKET_CREATE,
        PermissionType.TICKET_EDIT,
        PermissionType.TICKET_ASSIGN,
        PermissionType.MESSAGE_VIEW,
        PermissionType.MESSAGE_SEND,
        PermissionType.REPORT_VIEW,
        PermissionType.RULE_VIEW,
        PermissionType.RULE_TEST,
        PermissionType.STAFF_VIEW,
    ],
    SystemRole.STAFF: [
        PermissionType.TICKET_VIEW,
        PermissionType.MESSAGE_VIEW,
        PermissionType.MESSAGE_SEND,
        PermissionType.REPORT_VIEW,
    ],
    SystemRole.READ_ONLY: [
        PermissionType.TICKET_VIEW,
        PermissionType.MESSAGE_VIEW,
        PermissionType.REPORT_VIEW,
    ],
}


class Permission(Base):
    """
    Permission model for defining granular permissions

    Attributes:
        id: Primary key
        name: Permission name (unique)
        description: Permission description
        category: Permission category for grouping
        created_at: Creation timestamp
    """

    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="general")

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Permission(name={self.name}, category={self.category})>"


class Role(Base):
    """
    Role model for managing user roles

    Attributes:
        id: Primary key
        hotel_id: Foreign key to hotel
        name: Role name
        permissions: JSON string of permission names
        is_system_role: Whether this is a system-defined role
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    hotel_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    permissions: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    is_system_role: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"
