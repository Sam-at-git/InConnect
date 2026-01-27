"""
Pydantic schemas for Hotel
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HotelBase(BaseModel):
    """Base Hotel schema"""

    name: str = Field(..., min_length=1, max_length=100)
    corp_id: str = Field(..., min_length=1, max_length=100)
    address: str | None = Field(None, max_length=500)
    contact_phone: str | None = Field(None, max_length=20)
    contact_person: str | None = Field(None, max_length=50)
    status: str = Field(default="active", max_length=20)


class HotelCreate(HotelBase):
    """Schema for creating a hotel"""

    pass


class HotelUpdate(BaseModel):
    """Schema for updating a hotel"""

    name: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = Field(None, max_length=500)
    contact_phone: str | None = Field(None, max_length=20)
    contact_person: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=20)


class HotelResponse(HotelBase):
    """Schema for hotel response"""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HotelListResponse(BaseModel):
    """Schema for hotel list response"""

    items: list[HotelResponse]
    total: int
    page: int
    page_size: int
    pages: int
