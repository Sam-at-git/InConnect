"""
Pydantic schemas for Message
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.message import MessageType, MessageDirection


class MessageBase(BaseModel):
    """Base Message schema"""

    conversation_id: str = Field(..., min_length=1)
    message_type: MessageType = Field(default=MessageType.TEXT)
    direction: MessageDirection = Field(default=MessageDirection.INBOUND)
    content: str | None = None
    media_url: str | None = None
    sender_id: str | None = Field(None, max_length=100)
    wechat_msg_id: str | None = Field(None, max_length=100)


class MessageCreate(MessageBase):
    """Schema for creating a message"""

    pass


class MessageResponse(MessageBase):
    """Schema for message response"""

    id: str
    is_read: bool
    sent_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageSendRequest(BaseModel):
    """Schema for sending a message"""

    conversation_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: MessageType = Field(default=MessageType.TEXT)
    media_url: str | None = None


class MessageSendResponse(BaseModel):
    """Schema for message send response"""

    message_id: str
    status: str
    wechat_msgid: str | None = None
