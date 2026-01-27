"""
System Configuration schemas
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class SystemConfigBase(BaseModel):
    """Base system config schema"""

    key: str = Field(..., max_length=100, description="Configuration key")
    value: Optional[dict[str, Any]] = Field(default=None, description="Configuration value")
    description: Optional[str] = Field(default=None, description="Configuration description")
    category: str = Field(default="general", max_length=50, description="Configuration category")


class SystemConfigCreate(SystemConfigBase):
    """Schema for creating system config"""

    pass


class SystemConfigUpdate(BaseModel):
    """Schema for updating system config"""

    value: Optional[dict[str, Any]] = None
    description: Optional[str] = None


class SystemConfigResponse(SystemConfigBase):
    """Schema for system config response"""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketCategoryConfig(BaseModel):
    """Ticket category configuration"""

    key: str
    label: str
    color: str
    sla_hours: Optional[int] = None
    is_enabled: bool = True


class PriorityConfig(BaseModel):
    """Priority level configuration"""

    key: str
    label: str
    color: str
    urgency_hours: Optional[int] = None
    is_enabled: bool = True


class RoutingRuleConfig(BaseModel):
    """Routing rule configuration"""

    id: str
    name: str
    conditions: dict[str, Any]
    action: dict[str, Any]
    priority: int
    is_enabled: bool
