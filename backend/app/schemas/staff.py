"""
Pydantic schemas for Staff
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, EmailStr

from app.models.staff import StaffRole, StaffStatus


class StaffBase(BaseModel):
    """Base Staff schema"""

    hotel_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=50)
    wechat_userid: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    role: StaffRole = Field(default=StaffRole.OTHER)
    department: str | None = Field(None, max_length=50)
    status: StaffStatus = Field(default=StaffStatus.ACTIVE)
    is_available: bool = True


class StaffCreate(StaffBase):
    """Schema for creating a staff member"""

    pass


class StaffUpdate(BaseModel):
    """Schema for updating a staff member"""

    name: str | None = Field(None, min_length=1, max_length=50)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    role: StaffRole | None = None
    department: str | None = Field(None, max_length=50)
    status: StaffStatus | None = None
    is_available: bool | None = None


class StaffResponse(StaffBase):
    """Schema for staff response"""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StaffListResponse(BaseModel):
    """Schema for staff list response"""

    items: list[StaffResponse]
    total: int
    page: int
    page_size: int
    pages: int
