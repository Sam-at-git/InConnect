"""
Report schemas for statistics and analytics
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class TimeRangeType(str, Enum):
    """Time range type for reports"""

    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    CUSTOM = "custom"


class TimeRangeRequest(BaseModel):
    """Time range filter request"""

    range_type: TimeRangeType = Field(default=TimeRangeType.THIS_WEEK)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class TicketStatusStats(BaseModel):
    """Ticket status statistics"""

    status: str
    count: int
    percentage: float


class TicketPriorityStats(BaseModel):
    """Ticket priority statistics"""

    priority: str
    count: int
    percentage: float


class TicketCategoryStats(BaseModel):
    """Ticket category statistics"""

    category: str
    count: int
    percentage: float


class TicketReport(BaseModel):
    """Ticket statistics report"""

    total: int
    by_status: list[TicketStatusStats]
    by_priority: list[TicketPriorityStats]
    by_category: list[TicketCategoryStats]
    created_in_period: int
    resolved_in_period: int
    closed_in_period: int
    avg_resolution_hours: Optional[float] = None
    overdue_count: int


class StaffPerformanceStats(BaseModel):
    """Staff performance statistics"""

    staff_id: str
    staff_name: str
    department: Optional[str] = None
    total_assigned: int
    total_resolved: int
    total_in_progress: int
    resolution_rate: float
    avg_resolution_hours: Optional[float] = None
    avg_response_hours: Optional[float] = None


class StaffReport(BaseModel):
    """Staff performance report"""

    total_staff: int
    staff_stats: list[StaffPerformanceStats]
    period_start: datetime
    period_end: datetime


class MessageTypeStats(BaseModel):
    """Message type statistics"""

    message_type: str
    count: int
    percentage: float


class MessageDirectionStats(BaseModel):
    """Message direction statistics"""

    direction: str
    count: int
    percentage: float


class MessageReport(BaseModel):
    """Message statistics report"""

    total: int
    by_type: list[MessageTypeStats]
    by_direction: list[MessageDirectionStats]
    avg_daily_count: float
    peak_conversations: int
    period_start: datetime
    period_end: datetime


class DashboardSummary(BaseModel):
    """Dashboard summary report"""

    total_tickets: int
    pending_tickets: int
    in_progress_tickets: int
    overdue_tickets: int
    total_messages: int
    unread_messages: int
    active_conversations: int
    available_staff: int
    period_start: datetime
    period_end: datetime
