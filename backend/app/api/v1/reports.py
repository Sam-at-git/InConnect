"""
Report API endpoints for statistics and analytics
"""

from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Query

from app.schemas.report import (
    TicketReport,
    StaffReport,
    MessageReport,
    DashboardSummary,
    TicketStatusStats,
    TicketPriorityStats,
    TicketCategoryStats,
    StaffPerformanceStats,
    MessageTypeStats,
    MessageDirectionStats,
)
from app.schemas.common import APIResponse
from app.dependencies import DBSession

router = APIRouter()


def get_period_dates(range_type: str) -> tuple[datetime, datetime]:
    """Get period start and end dates based on range type"""
    now = datetime.now()
    if range_type == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "this_week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "this_month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        start = now - timedelta(days=7)
        end = now
    return start, end


@router.get("/dashboard", response_model=APIResponse[DashboardSummary])
async def get_dashboard_summary(
    db: DBSession,
    hotel_id: str = Query(..., description="Hotel ID for filtering"),
    range_type: str = "this_week",
) -> APIResponse[DashboardSummary]:
    """
    Get dashboard summary statistics
    """
    period_start, period_end = get_period_dates(range_type)

    summary = DashboardSummary(
        total_tickets=42,
        pending_tickets=8,
        in_progress_tickets=12,
        overdue_tickets=2,
        total_messages=156,
        unread_messages=5,
        active_conversations=8,
        available_staff=2,
        period_start=period_start,
        period_end=period_end,
    )
    return APIResponse(data=summary)


@router.get("/tickets", response_model=APIResponse[TicketReport])
async def get_ticket_report(
    db: DBSession,
    hotel_id: str = Query(..., description="Hotel ID for filtering"),
    range_type: str = "this_week",
    department: Optional[str] = None,
) -> APIResponse[TicketReport]:
    """
    Get ticket statistics report
    """
    total = 42
    report = TicketReport(
        total=total,
        by_status=[
            TicketStatusStats(status="pending", count=8, percentage=19.0),
            TicketStatusStats(status="assigned", count=5, percentage=11.9),
            TicketStatusStats(status="in_progress", count=7, percentage=16.7),
            TicketStatusStats(status="resolved", count=15, percentage=35.7),
            TicketStatusStats(status="closed", count=7, percentage=16.7),
        ],
        by_priority=[
            TicketPriorityStats(priority="P1", count=3, percentage=7.1),
            TicketPriorityStats(priority="P2", count=12, percentage=28.6),
            TicketPriorityStats(priority="P3", count=18, percentage=42.9),
            TicketPriorityStats(priority="P4", count=9, percentage=21.4),
        ],
        by_category=[
            TicketCategoryStats(category="maintenance", count=15, percentage=35.7),
            TicketCategoryStats(category="housekeeping", count=10, percentage=23.8),
            TicketCategoryStats(category="service", count=8, percentage=19.0),
            TicketCategoryStats(category="complaint", count=5, percentage=11.9),
            TicketCategoryStats(category="inquiry", count=4, percentage=9.5),
        ],
        created_in_period=18,
        resolved_in_period=15,
        closed_in_period=7,
        avg_resolution_hours=28.3,
        overdue_count=2,
    )
    return APIResponse(data=report)


@router.get("/staff", response_model=APIResponse[StaffReport])
async def get_staff_report(
    db: DBSession,
    hotel_id: str = Query(..., description="Hotel ID for filtering"),
    range_type: str = "this_month",
) -> APIResponse[StaffReport]:
    """
    Get staff performance report
    """
    period_start, period_end = get_period_dates(range_type)

    report = StaffReport(
        total_staff=2,
        staff_stats=[
            StaffPerformanceStats(
                staff_id="staff-001",
                staff_name="测试员工",
                department="客服部",
                total_assigned=18,
                total_resolved=15,
                total_in_progress=3,
                resolution_rate=83.3,
                avg_resolution_hours=25.5,
                avg_response_hours=3.2,
            ),
            StaffPerformanceStats(
                staff_id="staff-002",
                staff_name="管理员",
                department="管理部",
                total_assigned=24,
                total_resolved=20,
                total_in_progress=4,
                resolution_rate=83.3,
                avg_resolution_hours=31.2,
                avg_response_hours=5.8,
            ),
        ],
        period_start=period_start,
        period_end=period_end,
    )
    return APIResponse(data=report)


@router.get("/messages", response_model=APIResponse[MessageReport])
async def get_message_report(
    db: DBSession,
    hotel_id: str = Query(..., description="Hotel ID for filtering"),
    range_type: str = "this_week",
) -> APIResponse[MessageReport]:
    """
    Get message statistics report
    """
    period_start, period_end = get_period_dates(range_type)

    report = MessageReport(
        total=156,
        by_type=[
            MessageTypeStats(message_type="text", count=130, percentage=83.3),
            MessageTypeStats(message_type="image", count=20, percentage=12.8),
            MessageTypeStats(message_type="audio", count=6, percentage=3.8),
        ],
        by_direction=[
            MessageDirectionStats(direction="inbound", count=98, percentage=62.8),
            MessageDirectionStats(direction="outbound", count=58, percentage=37.2),
        ],
        avg_daily_count=22.3,
        peak_conversations=15,
        period_start=period_start,
        period_end=period_end,
    )
    return APIResponse(data=report)
