"""
Report API endpoints for statistics and analytics
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.report import (
    TimeRangeRequest,
    TicketReport,
    StaffReport,
    MessageReport,
    DashboardSummary,
)
from app.schemas.common import APIResponse
from app.core.auth import get_current_user_id
from app.dependencies import DBSession
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/dashboard", response_model=APIResponse[DashboardSummary])
def get_dashboard_summary(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID for filtering")] = ...,
    range_type: str = "this_week",
) -> APIResponse[DashboardSummary]:
    """
    Get dashboard summary statistics

    Args:
        db: Database session
        hotel_id: Hotel ID for filtering
        range_type: Time range type (today/yesterday/this_week/last_week/this_month/last_month)

    Returns:
        Dashboard summary with key metrics
    """
    range_request = TimeRangeRequest(range_type=range_type)
    summary = ReportService.get_dashboard_summary(db, hotel_id, range_request)

    return APIResponse(data=summary)


@router.get("/tickets", response_model=APIResponse[TicketReport])
def get_ticket_report(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID for filtering")] = ...,
    range_type: str = "this_week",
    department: Optional[str] = None,
) -> APIResponse[TicketReport]:
    """
    Get ticket statistics report

    Args:
        db: Database session
        hotel_id: Hotel ID for filtering
        range_type: Time range type
        department: Optional filter by department/category

    Returns:
        Ticket statistics including status, priority, and category breakdowns
    """
    range_request = TimeRangeRequest(range_type=range_type)
    report = ReportService.get_ticket_report(db, hotel_id, range_request, department)

    return APIResponse(data=report)


@router.get("/staff", response_model=APIResponse[StaffReport])
def get_staff_report(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID for filtering")] = ...,
    range_type: str = "this_month",
) -> APIResponse[StaffReport]:
    """
    Get staff performance report

    Args:
        db: Database session
        hotel_id: Hotel ID for filtering
        range_type: Time range type

    Returns:
        Staff performance metrics including resolution rates and response times
    """
    range_request = TimeRangeRequest(range_type=range_type)
    report = ReportService.get_staff_report(db, hotel_id, range_request)

    return APIResponse(data=report)


@router.get("/messages", response_model=APIResponse[MessageReport])
def get_message_report(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID for filtering")] = ...,
    range_type: str = "this_week",
) -> APIResponse[MessageReport]:
    """
    Get message statistics report

    Args:
        db: Database session
        hotel_id: Hotel ID for filtering
        range_type: Time range type

    Returns:
        Message statistics including type and direction breakdowns
    """
    range_request = TimeRangeRequest(range_type=range_type)
    report = ReportService.get_message_report(db, hotel_id, range_request)

    return APIResponse(data=report)
