"""
Report service for generating statistics and analytics
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy import select, func, case, and_
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory
from app.models.message import Message, MessageType, MessageDirection
from app.models.staff import Staff, StaffStatus
from app.models.conversation import Conversation
from app.schemas.report import (
    TimeRangeRequest,
    TicketReport,
    TicketStatusStats,
    TicketPriorityStats,
    TicketCategoryStats,
    StaffReport,
    StaffPerformanceStats,
    MessageReport,
    MessageTypeStats,
    MessageDirectionStats,
    DashboardSummary,
    TimeRangeType,
)


class ReportService:
    """Service for generating reports and statistics"""

    @staticmethod
    def _get_date_range(range_request: TimeRangeRequest) -> tuple[datetime, datetime]:
        """Calculate start and end dates based on range type"""
        now = datetime.now(timezone.utc)
        range_type = range_request.range_type

        if range_type == TimeRangeType.TODAY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif range_type == TimeRangeType.YESTERDAY:
            yesterday = now - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif range_type == TimeRangeType.THIS_WEEK:
            start = (now - timedelta(days=now.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = now
        elif range_type == TimeRangeType.LAST_WEEK:
            start = (now - timedelta(days=now.weekday() + 7)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = (now - timedelta(days=now.weekday() + 1)).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif range_type == TimeRangeType.THIS_MONTH:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif range_type == TimeRangeType.LAST_MONTH:
            start = (now.replace(day=1) - timedelta(days=1)).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(
                seconds=1
            )
        else:  # CUSTOM
            start = range_request.start_date or now - timedelta(days=7)
            end = range_request.end_date or now

        return start, end

    @staticmethod
    def get_ticket_report(
        db: Session, hotel_id: str, range_request: TimeRangeRequest, department: Optional[str] = None
    ) -> TicketReport:
        """Generate ticket statistics report"""
        start, end = ReportService._get_date_range(range_request)

        # Base query with filters
        base_filters = [Ticket.hotel_id == hotel_id]
        if department:
            base_filters.append(Ticket.category == department)

        # Total tickets
        total_query = select(func.count(Ticket.id)).where(and_(*base_filters))
        total = db.execute(total_query).scalar() or 0

        # By status
        status_query = (
            select(
                Ticket.status,
                func.count(Ticket.id).label("count"),
            )
            .where(and_(*base_filters))
            .group_by(Ticket.status)
        )
        status_results = db.execute(status_query).all()
        by_status = [
            TicketStatusStats(
                status=row.status,
                count=row.count,
                percentage=round((row.count / total * 100) if total > 0 else 0, 2),
            )
            for row in status_results
        ]

        # By priority
        priority_query = (
            select(
                Ticket.priority,
                func.count(Ticket.id).label("count"),
            )
            .where(and_(*base_filters))
            .group_by(Ticket.priority)
        )
        priority_results = db.execute(priority_query).all()
        by_priority = [
            TicketPriorityStats(
                priority=row.priority,
                count=row.count,
                percentage=round((row.count / total * 100) if total > 0 else 0, 2),
            )
            for row in priority_results
        ]

        # By category
        category_query = (
            select(
                Ticket.category,
                func.count(Ticket.id).label("count"),
            )
            .where(and_(*base_filters))
            .group_by(Ticket.category)
        )
        category_results = db.execute(category_query).all()
        by_category = [
            TicketCategoryStats(
                category=row.category,
                count=row.count,
                percentage=round((row.count / total * 100) if total > 0 else 0, 2),
            )
            for row in category_results
        ]

        # Created in period
        created_query = select(func.count(Ticket.id)).where(
            and_(*base_filters, Ticket.created_at >= start, Ticket.created_at <= end)
        )
        created_in_period = db.execute(created_query).scalar() or 0

        # Resolved in period
        resolved_query = select(func.count(Ticket.id)).where(
            and_(
                *base_filters,
                Ticket.resolved_at.isnot(None),
                Ticket.resolved_at >= start,
                Ticket.resolved_at <= end,
            )
        )
        resolved_in_period = db.execute(resolved_query).scalar() or 0

        # Closed in period
        closed_query = select(func.count(Ticket.id)).where(
            and_(
                *base_filters,
                Ticket.closed_at.isnot(None),
                Ticket.closed_at >= start,
                Ticket.closed_at <= end,
            )
        )
        closed_in_period = db.execute(closed_query).scalar() or 0

        # Average resolution time (in hours)
        avg_time_query = select(
            func.avg(
                func.extract(
                    "epoch",
                    case(
                        (Ticket.resolved_at.isnot(None), Ticket.resolved_at - Ticket.created_at),
                        else_=None,
                    ),
                )
            )
            / 3600
        ).where(
            and_(*base_filters, Ticket.resolved_at.isnot(None))
        )
        avg_resolution_hours = db.execute(avg_time_query).scalar()

        # Overdue count
        overdue_query = select(func.count(Ticket.id)).where(
            and_(
                *base_filters,
                Ticket.due_at < datetime.now(timezone.utc),
                Ticket.status.notin_([TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value]),
            )
        )
        overdue_count = db.execute(overdue_query).scalar() or 0

        return TicketReport(
            total=total,
            by_status=by_status,
            by_priority=by_priority,
            by_category=by_category,
            created_in_period=created_in_period,
            resolved_in_period=resolved_in_period,
            closed_in_period=closed_in_period,
            avg_resolution_hours=round(avg_resolution_hours, 2) if avg_resolution_hours else None,
            overdue_count=overdue_count,
        )

    @staticmethod
    def get_staff_report(
        db: Session, hotel_id: str, range_request: TimeRangeRequest
    ) -> StaffReport:
        """Generate staff performance report"""
        start, end = ReportService._get_date_range(range_request)

        # Get all active staff
        staff_query = select(Staff).where(
            and_(Staff.hotel_id == hotel_id, Staff.status == StaffStatus.ACTIVE.value)
        )
        staff_members = db.execute(staff_query).scalars().all()

        staff_stats = []

        for staff in staff_members:
            # Total assigned
            total_assigned_query = select(func.count(Ticket.id)).where(
                Ticket.assigned_to == staff.id
            )
            total_assigned = db.execute(total_assigned_query).scalar() or 0

            # Total resolved
            total_resolved_query = select(func.count(Ticket.id)).where(
                and_(
                    Ticket.assigned_to == staff.id,
                    Ticket.status == TicketStatus.RESOLVED.value,
                )
            )
            total_resolved = db.execute(total_resolved_query).scalar() or 0

            # Total in progress
            total_in_progress_query = select(func.count(Ticket.id)).where(
                and_(
                    Ticket.assigned_to == staff.id,
                    Ticket.status == TicketStatus.IN_PROGRESS.value,
                )
            )
            total_in_progress = db.execute(total_in_progress_query).scalar() or 0

            # Resolution rate
            resolution_rate = (
                round((total_resolved / total_assigned * 100), 2) if total_assigned > 0 else 0
            )

            # Average resolution time
            avg_resolution_query = select(
                func.avg(
                    func.extract("epoch", Ticket.resolved_at - Ticket.created_at)
                )
                / 3600
            ).where(
                and_(
                    Ticket.assigned_to == staff.id,
                    Ticket.resolved_at.isnot(None),
                )
            )
            avg_resolution_hours = db.execute(avg_resolution_query).scalar()

            # Average response time (time from ticket creation to first assignment)
            avg_response_query = select(
                func.avg(
                    func.extract("epoch", Ticket.updated_at - Ticket.created_at)
                )
                / 3600
            ).where(
                and_(
                    Ticket.assigned_to == staff.id,
                    Ticket.assigned_to.isnot(None),
                )
            )
            avg_response_hours = db.execute(avg_response_query).scalar()

            staff_stats.append(
                StaffPerformanceStats(
                    staff_id=staff.id,
                    staff_name=staff.name,
                    department=staff.department,
                    total_assigned=total_assigned,
                    total_resolved=total_resolved,
                    total_in_progress=total_in_progress,
                    resolution_rate=resolution_rate,
                    avg_resolution_hours=round(avg_resolution_hours, 2) if avg_resolution_hours else None,
                    avg_response_hours=round(avg_response_hours, 2) if avg_response_hours else None,
                )
            )

        return StaffReport(
            total_staff=len(staff_members),
            staff_stats=staff_stats,
            period_start=start,
            period_end=end,
        )

    @staticmethod
    def get_message_report(
        db: Session, hotel_id: str, range_request: TimeRangeRequest
    ) -> MessageReport:
        """Generate message statistics report"""
        start, end = ReportService._get_date_range(range_request)

        # Get conversation IDs for this hotel
        conv_query = select(Conversation.id).where(Conversation.hotel_id == hotel_id)
        conversation_ids = [row[0] for row in db.execute(conv_query).all()]

        if not conversation_ids:
            return MessageReport(
                total=0,
                by_type=[],
                by_direction=[],
                avg_daily_count=0,
                peak_conversations=0,
                period_start=start,
                period_end=end,
            )

        # Total messages in period
        total_query = select(func.count(Message.id)).where(
            and_(
                Message.conversation_id.in_(conversation_ids),
                Message.created_at >= start,
                Message.created_at <= end,
            )
        )
        total = db.execute(total_query).scalar() or 0

        # By type
        type_query = (
            select(Message.message_type, func.count(Message.id).label("count"))
            .where(
                and_(
                    Message.conversation_id.in_(conversation_ids),
                    Message.created_at >= start,
                    Message.created_at <= end,
                )
            )
            .group_by(Message.message_type)
        )
        type_results = db.execute(type_query).all()
        by_type = [
            MessageTypeStats(
                message_type=row.message_type,
                count=row.count,
                percentage=round((row.count / total * 100) if total > 0 else 0, 2),
            )
            for row in type_results
        ]

        # By direction
        direction_query = (
            select(Message.direction, func.count(Message.id).label("count"))
            .where(
                and_(
                    Message.conversation_id.in_(conversation_ids),
                    Message.created_at >= start,
                    Message.created_at <= end,
                )
            )
            .group_by(Message.direction)
        )
        direction_results = db.execute(direction_query).all()
        by_direction = [
            MessageDirectionStats(
                direction=row.direction,
                count=row.count,
                percentage=round((row.count / total * 100) if total > 0 else 0, 2),
            )
            for row in direction_results
        ]

        # Average daily count
        days_diff = max(1, (end - start).days)
        avg_daily_count = round(total / days_diff, 2)

        # Peak conversations (active conversations in period)
        peak_query = (
            select(func.count(func.distinct(Message.conversation_id)))
            .where(
                and_(
                    Message.conversation_id.in_(conversation_ids),
                    Message.created_at >= start,
                    Message.created_at <= end,
                )
            )
        )
        peak_conversations = db.execute(peak_query).scalar() or 0

        return MessageReport(
            total=total,
            by_type=by_type,
            by_direction=by_direction,
            avg_daily_count=avg_daily_count,
            peak_conversations=peak_conversations,
            period_start=start,
            period_end=end,
        )

    @staticmethod
    def get_dashboard_summary(
        db: Session, hotel_id: str, range_request: TimeRangeRequest
    ) -> DashboardSummary:
        """Generate dashboard summary"""
        start, end = ReportService._get_date_range(range_request)

        # Total tickets
        total_tickets_query = select(func.count(Ticket.id)).where(Ticket.hotel_id == hotel_id)
        total_tickets = db.execute(total_tickets_query).scalar() or 0

        # Pending tickets
        pending_tickets_query = select(func.count(Ticket.id)).where(
            and_(
                Ticket.hotel_id == hotel_id,
                Ticket.status == TicketStatus.PENDING.value,
            )
        )
        pending_tickets = db.execute(pending_tickets_query).scalar() or 0

        # In progress tickets
        in_progress_tickets_query = select(func.count(Ticket.id)).where(
            and_(
                Ticket.hotel_id == hotel_id,
                Ticket.status == TicketStatus.IN_PROGRESS.value,
            )
        )
        in_progress_tickets = db.execute(in_progress_tickets_query).scalar() or 0

        # Overdue tickets
        overdue_tickets_query = select(func.count(Ticket.id)).where(
            and_(
                Ticket.hotel_id == hotel_id,
                Ticket.due_at < datetime.now(timezone.utc),
                Ticket.status.notin_([TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value]),
            )
        )
        overdue_tickets = db.execute(overdue_tickets_query).scalar() or 0

        # Total messages
        conv_query = select(Conversation.id).where(Conversation.hotel_id == hotel_id)
        conversation_ids = [row[0] for row in db.execute(conv_query).all()]

        if conversation_ids:
            total_messages_query = select(func.count(Message.id)).where(
                Message.conversation_id.in_(conversation_ids)
            )
            total_messages = db.execute(total_messages_query).scalar() or 0

            # Unread messages
            unread_messages_query = select(func.count(Message.id)).where(
                and_(
                    Message.conversation_id.in_(conversation_ids),
                    Message.direction == MessageDirection.INBOUND.value,
                    Message.is_read == False,
                )
            )
            unread_messages = db.execute(unread_messages_query).scalar() or 0
        else:
            total_messages = 0
            unread_messages = 0

        # Active conversations
        active_conversations = len(conversation_ids)

        # Available staff
        available_staff_query = select(func.count(Staff.id)).where(
            and_(
                Staff.hotel_id == hotel_id,
                Staff.status == StaffStatus.ACTIVE.value,
                Staff.is_available == True,
            )
        )
        available_staff = db.execute(available_staff_query).scalar() or 0

        return DashboardSummary(
            total_tickets=total_tickets,
            pending_tickets=pending_tickets,
            in_progress_tickets=in_progress_tickets,
            overdue_tickets=overdue_tickets,
            total_messages=total_messages,
            unread_messages=unread_messages,
            active_conversations=active_conversations,
            available_staff=available_staff,
            period_start=start,
            period_end=end,
        )
