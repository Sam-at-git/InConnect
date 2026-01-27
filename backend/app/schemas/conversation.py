"""
Pydantic schemas for Conversation
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConversationBase(BaseModel):
    """Base Conversation schema"""

    hotel_id: str = Field(..., min_length=1)
    guest_id: str = Field(..., min_length=1)
    guest_name: str | None = Field(None, max_length=50)
    guest_phone: str | None = Field(None, max_length=20)
    guest_avatar: str | None = None
    status: str = Field(default="active", max_length=20)


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation"""

    pass


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation"""

    guest_name: str | None = Field(None, max_length=50)
    guest_phone: str | None = Field(None, max_length=20)
    guest_avatar: str | None = None
    status: str | None = Field(None, max_length=20)


class ConversationResponse(ConversationBase):
    """Schema for conversation response"""

    id: str
    last_message_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
