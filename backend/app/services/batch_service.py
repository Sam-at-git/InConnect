"""
Batch operation service for tickets
"""

from typing import List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.ticket import Ticket
from app.models.ticket_timeline import TicketTimeline, TimelineEventType
from app.models.staff import Staff
from app.schemas.batch import BatchOperationResult


class BatchOperationService:
    """Service for batch operations on tickets"""

    @staticmethod
    def batch_assign_tickets(
        db: Session, ticket_ids: List[str], staff_id: str, comment: str | None = None
    ) -> BatchOperationResult:
        """
        Batch assign tickets to a staff member

        Args:
            db: Database session
            ticket_ids: List of ticket IDs to assign
            staff_id: Staff ID to assign tickets to
            comment: Optional comment for the timeline

        Returns:
            Batch operation result
        """
        # Verify staff exists
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            return BatchOperationResult(
                success_count=0,
                failed_count=len(ticket_ids),
                failed_ids=ticket_ids,
                errors=[f"Staff {staff_id} not found"],
            )

        success_count = 0
        failed_count = 0
        failed_ids: List[str] = []
        errors: List[str] = []

        for ticket_id in ticket_ids:
            try:
                ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
                if not ticket:
                    failed_count += 1
                    failed_ids.append(ticket_id)
                    errors.append(f"Ticket {ticket_id} not found")
                    continue

                # Update ticket
                old_assignee = ticket.assigned_to
                ticket.assigned_to = staff_id
                ticket.status = "assigned"

                # Create timeline entry
                timeline = TicketTimeline(
                    ticket_id=ticket_id,
                    staff_id=staff_id,
                    event_type=TimelineEventType.ASSIGNED.value,
                    old_value=old_assignee,
                    new_value=staff_id,
                    comment=comment,
                )
                db.add(timeline)

                success_count += 1
            except Exception as e:
                failed_count += 1
                failed_ids.append(ticket_id)
                errors.append(f"Ticket {ticket_id}: {str(e)}")

        db.commit()
        return BatchOperationResult(
            success_count=success_count,
            failed_count=failed_count,
            failed_ids=failed_ids,
            errors=errors,
        )

    @staticmethod
    def batch_update_status(
        db: Session, ticket_ids: List[str], status: str, comment: str | None = None
    ) -> BatchOperationResult:
        """
        Batch update ticket status

        Args:
            db: Database session
            ticket_ids: List of ticket IDs to update
            status: New status
            comment: Optional comment for the timeline

        Returns:
            Batch operation result
        """
        success_count = 0
        failed_count = 0
        failed_ids: List[str] = []
        errors: List[str] = []

        for ticket_id in ticket_ids:
            try:
                ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
                if not ticket:
                    failed_count += 1
                    failed_ids.append(ticket_id)
                    errors.append(f"Ticket {ticket_id} not found")
                    continue

                # Update ticket
                old_status = ticket.status
                ticket.status = status

                # Update timestamps based on status
                now = datetime.utcnow()
                if status == "resolved":
                    ticket.resolved_at = now
                elif status == "closed":
                    ticket.closed_at = now

                # Create timeline entry
                timeline = TicketTimeline(
                    ticket_id=ticket_id,
                    event_type=TimelineEventType.STATUS_CHANGED.value,
                    old_value=old_status,
                    new_value=status,
                    comment=comment,
                )
                db.add(timeline)

                success_count += 1
            except Exception as e:
                failed_count += 1
                failed_ids.append(ticket_id)
                errors.append(f"Ticket {ticket_id}: {str(e)}")

        db.commit()
        return BatchOperationResult(
            success_count=success_count,
            failed_count=failed_count,
            failed_ids=failed_ids,
            errors=errors,
        )

    @staticmethod
    def get_tickets_for_export(
        db: Session,
        hotel_id: str,
        status: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> List[Ticket]:
        """
        Get tickets for export based on filters

        Args:
            db: Database session
            hotel_id: Hotel ID
            status: Optional status filter
            priority: Optional priority filter
            category: Optional category filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of tickets matching filters
        """
        query = db.query(Ticket).filter(Ticket.hotel_id == hotel_id)

        if status:
            query = query.filter(Ticket.status == status)
        if priority:
            query = query.filter(Ticket.priority == priority)
        if category:
            query = query.filter(Ticket.category == category)
        if start_date:
            query = query.filter(Ticket.created_at >= start_date)
        if end_date:
            query = query.filter(Ticket.created_at <= end_date)

        return query.all()

    @staticmethod
    def export_tickets_to_csv(tickets: List[Ticket]) -> str:
        """
        Export tickets to CSV format

        Args:
            tickets: List of tickets to export

        Returns:
            CSV formatted string
        """
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "工单ID",
                "标题",
                "描述",
                "分类",
                "优先级",
                "状态",
                "分配给",
                "创建时间",
                "更新时间",
                "截止时间",
                "解决时间",
                "关闭时间",
            ]
        )

        # Write data
        for ticket in tickets:
            writer.writerow(
                [
                    ticket.id,
                    ticket.title,
                    ticket.description or "",
                    ticket.category,
                    ticket.priority,
                    ticket.status,
                    ticket.assigned_to or "",
                    ticket.created_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.created_at else "",
                    ticket.updated_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.updated_at else "",
                    ticket.due_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.due_at else "",
                    ticket.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.resolved_at else "",
                    ticket.closed_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.closed_at else "",
                ]
            )

        return output.getvalue()


batch_service = BatchOperationService()
