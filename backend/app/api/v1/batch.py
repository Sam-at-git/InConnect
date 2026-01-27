"""
Batch operation API endpoints
"""

from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.schemas.batch import (
    BatchAssignRequest,
    BatchStatusUpdateRequest,
    BatchOperationResult,
    TicketExportRequest,
)
from app.schemas.common import APIResponse
from app.dependencies import DBSession
from app.services.batch_service import batch_service

router = APIRouter()


@router.post("/assign", response_model=APIResponse[BatchOperationResult])
def batch_assign_tickets(
    request: BatchAssignRequest,
    db: Session = Depends(DBSession),
) -> APIResponse[BatchOperationResult]:
    """
    Batch assign tickets to a staff member

    Args:
        request: Batch assign request with ticket IDs and staff ID
        db: Database session

    Returns:
        Batch operation result with success/failure counts
    """
    result = batch_service.batch_assign_tickets(
        db, request.ticket_ids, request.staff_id, request.comment
    )
    return APIResponse(data=result)


@router.post("/status", response_model=APIResponse[BatchOperationResult])
def batch_update_status(
    request: BatchStatusUpdateRequest,
    db: Session = Depends(DBSession),
) -> APIResponse[BatchOperationResult]:
    """
    Batch update ticket status

    Args:
        request: Batch status update request with ticket IDs and new status
        db: Database session

    Returns:
        Batch operation result with success/failure counts
    """
    result = batch_service.batch_update_status(
        db, request.ticket_ids, request.status, request.comment
    )
    return APIResponse(data=result)


@router.post("/export")
def export_tickets(
    hotel_id: Annotated[str, Query(description="Hotel ID for filtering")] = ...,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    format: str = "csv",
    db: Session = Depends(DBSession),
) -> Response:
    """
    Export tickets to CSV or Excel format

    Args:
        hotel_id: Hotel ID for filtering
        status: Optional status filter
        priority: Optional priority filter
        category: Optional category filter
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)
        format: Export format (csv or excel)
        db: Database session

    Returns:
        File with exported data
    """
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    # Get tickets
    tickets = batch_service.get_tickets_for_export(
        db, hotel_id, status, priority, category, start_dt, end_dt
    )

    if format == "csv":
        csv_data = batch_service.export_tickets_to_csv(tickets)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=tickets_{hotel_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            },
        )

    # Excel format would require additional library (openpyxl/xlsxwriter)
    # For MVP, return CSV for both formats
    csv_data = batch_service.export_tickets_to_csv(tickets)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=tickets_{hotel_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )
