"""
Audit Log API endpoints
"""

from typing import Annotated, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.common import APIResponse
from app.dependencies import DBSession
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("", response_model=APIResponse[List[dict]])
def get_audit_logs(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID")] = ...,
    staff_id: Annotated[Optional[str], Query(description="Filter by staff ID")] = None,
    action: Annotated[Optional[str], Query(description="Filter by action")] = None,
    resource_type: Annotated[Optional[str], Query(description="Filter by resource type")] = None,
    start_date: Annotated[Optional[str], Query(description="Start date (ISO format)")] = None,
    end_date: Annotated[Optional[str], Query(description="End date (ISO format)")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> APIResponse[List[dict]]:
    """
    Get audit logs with filters

    Args:
        db: Database session
        hotel_id: Hotel ID
        staff_id: Optional staff ID filter
        action: Optional action filter
        resource_type: Optional resource type filter
        start_date: Optional start date
        end_date: Optional end date
        limit: Maximum records to return

    Returns:
        List of audit log entries
    """
    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    logs = audit_service.get_logs(
        db,
        hotel_id,
        staff_id=staff_id,
        action=action,
        resource_type=resource_type,
        start_date=start_dt,
        end_date=end_dt,
        limit=limit,
    )

    # Get staff names
    staff_ids = list(set([log.staff_id for log in logs if log.staff_id]))
    staff_map = {}
    if staff_ids:
        from app.models.staff import Staff
        staff_results = db.query(Staff).filter(Staff.id.in_(staff_ids)).all()
        staff_map = {s.id: s.name for s in staff_results}

    return APIResponse(data=[
        {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "staff_id": log.staff_id,
            "staff_name": staff_map.get(log.staff_id) or "Unknown",
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ])


@router.get("/summary", response_model=APIResponse[dict])
def get_audit_summary(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID")] = ...,
    days: Annotated[int, Query(ge=1, le=90)] = 7,
) -> APIResponse[dict]:
    """
    Get audit log summary for recent period

    Args:
        db: Database session
        hotel_id: Hotel ID
        days: Number of days to summarize

    Returns:
        Summary with action counts
    """
    from datetime import timedelta
    from sqlalchemy import func

    start_date = datetime.utcnow() - timedelta(days=days)

    # Count logs by action
    from app.models.audit_log import AuditLog

    action_counts = (
        db.query(AuditLog.action, func.count(AuditLog.id))
        .filter(
            AuditLog.hotel_id == hotel_id,
            AuditLog.created_at >= start_date,
        )
        .group_by(AuditLog.action)
        .all()
    )

    # Count logs by resource type
    resource_counts = (
        db.query(AuditLog.resource_type, func.count(AuditLog.id))
        .filter(
            AuditLog.hotel_id == hotel_id,
            AuditLog.created_at >= start_date,
        )
        .group_by(AuditLog.resource_type)
        .all()
    )

    # Total count
    total_count = (
        db.query(func.count(AuditLog.id))
        .filter(
            AuditLog.hotel_id == hotel_id,
            AuditLog.created_at >= start_date,
        )
        .scalar()
    )

    return APIResponse(data={
        "period_days": days,
        "total_actions": total_count or 0,
        "by_action": [
            {"action": action, "count": count}
            for action, count in action_counts
        ],
        "by_resource": [
            {"resource_type": resource, "count": count}
            for resource, count in resource_counts
        ],
    })


@router.get("/login-history", response_model=APIResponse[List[dict]])
def get_login_history(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID")] = ...,
    staff_id: Annotated[Optional[str], Query(description="Filter by staff ID")] = None,
    days: Annotated[int, Query(ge=1, le=90)] = 30,
) -> APIResponse[List[dict]]:
    """
    Get login/logout history

    Args:
        db: Database session
        hotel_id: Hotel ID
        staff_id: Optional staff ID filter
        days: Number of days to look back

    Returns:
        List of login events
    """
    history = audit_service.get_login_history(
        db,
        hotel_id,
        staff_id=staff_id,
        days=days,
    )

    return APIResponse(data=history)


@router.get("/export", response_model=APIResponse[str])
def export_audit_logs(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID")] = ...,
    start_date: Annotated[Optional[str], Query(description="Start date")] = None,
    end_date: Annotated[Optional[str], Query(description="End date")] = None,
) -> APIResponse[str]:
    """
    Export audit logs as CSV

    Args:
        db: Database session
        hotel_id: Hotel ID
        start_date: Optional start date
        end_date: Optional end date

    Returns:
        CSV data as string
    """
    import csv
    from io import StringIO

    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    logs = audit_service.get_logs(
        db,
        hotel_id,
        start_date=start_dt,
        end_date=end_dt,
        limit=10000,
    )

    # Get staff names
    staff_ids = list(set([log.staff_id for log in logs if log.staff_id]))
    staff_map = {}
    if staff_ids:
        from app.models.staff import Staff
        staff_results = db.query(Staff).filter(Staff.id.in_(staff_ids)).all()
        staff_map = {s.id: s.name for s in staff_results}

    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "时间",
        "操作",
        "资源类型",
        "资源ID",
        "操作人",
        "IP地址",
    ])

    for log in logs:
        writer.writerow([
            log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "",
            log.action,
            log.resource_type,
            log.resource_id or "",
            staff_map.get(log.staff_id) or "Unknown",
            log.ip_address or "",
        ])

    return APIResponse(data=output.getvalue())
