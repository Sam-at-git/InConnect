"""
Pydantic schemas for SLA (Service Level Agreement)
"""

from datetime import datetime
from typing import Literal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketPriority


class SLAStatus(str, Enum):
    """SLA status enum"""

    NORMAL = "normal"           # On track
    WARNING = "warning"         # Approaching deadline
    BREACHED = "breached"       # Past due
    RESOLVED = "resolved"       # Resolved within SLA


class SLAConfigBase(BaseModel):
    """Base SLA Config schema"""

    hotel_id: str | None = Field(None, min_length=1)
    priority: TicketPriority = Field(..., description="Ticket priority level")
    response_minutes: int = Field(..., ge=1, le=1440, description="Response time in minutes (max 24 hours)")
    resolution_minutes: int = Field(..., ge=1, le=10080, description="Resolution time in minutes (max 7 days)")
    is_active: bool = Field(default=True)


class SLAConfigCreate(SLAConfigBase):
    """Schema for creating SLA configuration"""

    pass


class SLAConfigUpdate(BaseModel):
    """Schema for updating SLA configuration"""

    response_minutes: int | None = Field(None, ge=1, le=1440)
    resolution_minutes: int | None = Field(None, ge=1, le=10080)
    is_active: bool | None = None


class SLAConfigResponse(SLAConfigBase):
    """Schema for SLA configuration response"""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SLATicketStatus(BaseModel):
    """SLA status for a specific ticket"""

    ticket_id: str
    status: SLAStatus
    response_target: datetime | None = Field(None, description="Target response time")
    resolution_target: datetime | None = Field(None, description="Target resolution time")
    minutes_remaining: int | None = Field(None, description="Minutes until deadline (negative if overdue)")
    percentage_used: float | None = Field(None, description="Percentage of SLA time used (0-100+, >100 means overdue)")


class SLAAlertType(str, Enum):
    """SLA alert type enum"""

    WARNING = "warning"         # Approaching deadline
    OVERDUE = "overdue"         # Past due
    ESCALATED = "escalated"     # Escalated to higher level


class SLAAlertResponse(BaseModel):
    """Schema for SLA alert response"""

    ticket_id: str
    ticket_title: str
    ticket_priority: TicketPriority
    alert_type: SLAAlertType
    hotel_id: str
    assigned_to: str | None
    due_at: datetime | None
    overdue_minutes: int | None = Field(None, description="Minutes overdue (if applicable)")
    escalation_level: int = Field(default=0, description="Current escalation level")
    message: str
    created_at: datetime


class SLAOverdueTicketsResponse(BaseModel):
    """Schema for overdue tickets response"""

    total: int
    items: list[SLATicketStatus]


class SLAStatsResponse(BaseModel):
    """Schema for SLA statistics response"""

    total_tickets: int
    normal_count: int
    warning_count: int
    breached_count: int
    resolved_count: int
    breach_rate: float = Field(description="Percentage of tickets that breached SLA")
    avg_response_time_minutes: float | None = Field(None, description="Average response time")
    avg_resolution_time_minutes: float | None = Field(None, description="Average resolution time")


class SLAConfigListResponse(BaseModel):
    """Schema for SLA config list response"""

    items: list[SLAConfigResponse]
    total: int
