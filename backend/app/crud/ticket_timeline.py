"""
CRUD operations for TicketTimeline model
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.ticket_timeline import TicketTimeline
from app.schemas.ticket_timeline import TicketTimelineCreate


class CRUDTicketTimeline(CRUDBase[TicketTimeline, TicketTimelineCreate, dict]):
    """CRUD operations for TicketTimeline"""

    async def get_by_ticket(
        self,
        db: AsyncSession,
        ticket_id: str,
        limit: int = 100,
    ) -> list[TicketTimeline]:
        """
        Get timeline entries for a ticket

        Args:
            db: Database session
            ticket_id: Ticket ID
            limit: Maximum records to return

        Returns:
            List of timeline entries
        """
        result = await db.execute(
            select(TicketTimeline)
            .filter(TicketTimeline.ticket_id == ticket_id)
            .order_by(TicketTimeline.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_timeline_entry(
        self,
        db: AsyncSession,
        ticket_id: str,
        event_type: str,
        staff_id: str | None,
        old_value: str | None = None,
        new_value: str | None = None,
        comment: str | None = None,
    ) -> TicketTimeline:
        """
        Create a timeline entry

        Args:
            db: Database session
            ticket_id: Ticket ID
            event_type: Event type
            staff_id: Staff ID who made the change
            old_value: Old value
            new_value: New value
            comment: Additional comment

        Returns:
            Created timeline entry
        """
        timeline_data = {
            "ticket_id": ticket_id,
            "staff_id": staff_id,
            "event_type": event_type,
            "old_value": old_value,
            "new_value": new_value,
            "comment": comment,
        }

        # Use dict instead of Pydantic model for timeline
        timeline = TicketTimeline(**timeline_data)
        db.add(timeline)
        await db.flush()
        await db.refresh(timeline)
        return timeline


# Create singleton instance
ticket_timeline = CRUDTicketTimeline(TicketTimeline)
