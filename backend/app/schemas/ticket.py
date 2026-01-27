"""
Pydantic schemas for Ticket
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketStatus, TicketPriority, TicketCategory


class TicketBase(BaseModel):
    """Base Ticket schema"""

    hotel_id: str = Field(..., min_length=1)
    conversation_id: str | None = Field(None, min_length=1)
    assigned_to: str | None = Field(None, min_length=1)
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    category: TicketCategory = Field(default=TicketCategory.OTHER)
    priority: TicketPriority = Field(default=TicketPriority.P3)
    due_at: datetime | None = None


class TicketCreate(TicketBase):
    """Schema for creating a ticket"""

    auto_assign: bool = False  # Whether to auto-assign the ticket


class TicketUpdate(BaseModel):
    """Schema for updating a ticket"""

    assigned_to: str | None = Field(None, min_length=1)
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    due_at: datetime | None = None


class TicketResponse(TicketBase):
    """Schema for ticket response"""

    id: str
    status: TicketStatus
    resolved_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketListResponse(BaseModel):
    """Schema for ticket list response"""

    items: list[TicketResponse]
    total: int
    page: int
    page_size: int
    pages: int


class TicketAssignRequest(BaseModel):
    """Schema for ticket assignment request"""

    staff_id: str = Field(..., min_length=1)
    comment: str | None = Field(None, max_length=500)


class TicketStatusUpdateRequest(BaseModel):
    """Schema for ticket status update request"""

    status: TicketStatus
    comment: str | None = Field(None, max_length=500)
