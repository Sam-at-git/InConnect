"""
Pydantic schemas for TicketTimeline
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TicketTimelineBase(BaseModel):
    """Base TicketTimeline schema"""

    ticket_id: str = Field(..., min_length=1)
    staff_id: str | None = None
    event_type: str = Field(..., min_length=1)
    old_value: str | None = None
    new_value: str | None = None
    comment: str | None = None


class TicketTimelineCreate(TicketTimelineBase):
    """Schema for creating a timeline entry"""

    pass


class TicketTimelineResponse(TicketTimelineBase):
    """Schema for timeline entry response"""

    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
