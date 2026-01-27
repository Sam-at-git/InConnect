"""
Audit logging service
"""

from typing import Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
import json

from app.models.audit_log import AuditLog, AuditAction
from app.models.staff import Staff


class AuditService:
    """Service for logging audit events"""

    @staticmethod
    def log_action(
        db: Session,
        hotel_id: str,
        action: AuditAction | str,
        resource_type: str,
        resource_id: str | None = None,
        staff_id: str | None = None,
        old_value: Any = None,
        new_value: Any = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """
        Log an audit action

        Args:
            db: Database session
            hotel_id: Hotel ID
            action: Action performed
            resource_type: Type of resource
            resource_id: ID of resource
            staff_id: Staff who performed the action
            old_value: Old value (for updates)
            new_value: New value
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Created audit log entry
        """
        # Convert complex values to JSON strings
        old_value_str = json.dumps(old_value) if old_value is not None else None
        new_value_str = json.dumps(new_value, ensure_ascii=False) if new_value is not None else None

        log_entry = AuditLog(
            hotel_id=hotel_id,
            staff_id=staff_id,
            action=action if isinstance(action, str) else action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value_str,
            new_value=new_value_str,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        return log_entry

    @staticmethod
    def log_ticket_action(
        db: Session,
        hotel_id: str,
        action: AuditAction,
        ticket_id: str,
        staff_id: str | None = None,
        changes: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """
        Log a ticket-related action

        Args:
            db: Database session
            hotel_id: Hotel ID
            action: Action performed
            ticket_id: Ticket ID
            staff_id: Staff who performed the action
            changes: Dictionary of changes made
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Created audit log entry
        """
        return AuditService.log_action(
            db=db,
            hotel_id=hotel_id,
            action=action,
            resource_type="ticket",
            resource_id=ticket_id,
            staff_id=staff_id,
            new_value=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def log_auth_action(
        db: Session,
        hotel_id: str,
        action: AuditAction,
        staff_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        success: bool = True,
    ) -> AuditLog:
        """
        Log an authentication action

        Args:
            db: Database session
            hotel_id: Hotel ID
            action: Action (login, logout, login_failed)
            staff_id: Staff ID
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether the action was successful

        Returns:
            Created audit log entry
        """
        return AuditService.log_action(
            db=db,
            hotel_id=hotel_id,
            action=action if success else AuditAction.LOGIN_FAILED,
            resource_type="auth",
            resource_id=staff_id,
            staff_id=staff_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def get_logs(
        db: Session,
        hotel_id: str,
        staff_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """
        Query audit logs with filters

        Args:
            db: Database session
            hotel_id: Hotel ID
            staff_id: Filter by staff ID
            action: Filter by action
            resource_type: Filter by resource type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum records to return

        Returns:
            List of audit log entries
        """
        from sqlalchemy import and_, or_

        query = db.query(AuditLog).filter(AuditLog.hotel_id == hotel_id)

        filters = []

        if staff_id:
            filters.append(AuditLog.staff_id == staff_id)

        if action:
            filters.append(AuditLog.action == action)

        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)

        if start_date:
            filters.append(AuditLog.created_at >= start_date)

        if end_date:
            filters.append(AuditLog.created_at <= end_date)

        if filters:
            query = query.filter(and_(*filters))

        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_login_history(
        db: Session,
        hotel_id: str,
        staff_id: str | None = None,
        days: int = 30,
    ) -> list[dict]:
        """
        Get login history for staff

        Args:
            db: Database session
            hotel_id: Hotel ID
            staff_id: Optional staff ID filter
            days: Number of days to look back

        Returns:
            List of login events with staff info
        """
        from datetime import timedelta
        from sqlalchemy import and_

        start_date = datetime.utcnow() - timedelta(days=days)

        query = (
            db.query(AuditLog, Staff)
            .outerjoin(Staff, AuditLog.staff_id == Staff.id)
            .filter(
                AuditLog.hotel_id == hotel_id,
                AuditLog.action.in_([
                    AuditAction.LOGIN.value,
                    AuditAction.LOGOUT.value,
                    AuditAction.LOGIN_FAILED.value,
                ]),
                AuditLog.created_at >= start_date,
            )
        )

        if staff_id:
            query = query.filter(AuditLog.staff_id == staff_id)

        results = query.order_by(AuditLog.created_at.desc()).limit(100).all()

        return [
            {
                "id": log.id,
                "action": log.action,
                "staff_id": log.staff_id,
                "staff_name": staff.name if staff else "Unknown",
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log, staff in results
        ]


audit_service = AuditService()
