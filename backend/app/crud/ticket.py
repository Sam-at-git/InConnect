"""
CRUD operations for Ticket model
"""

from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate


class CRUDTicket(CRUDBase[Ticket, TicketCreate, TicketUpdate]):
    """CRUD operations for Ticket"""

    async def get_by_hotel(
        self,
        db: AsyncSession,
        hotel_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Ticket]:
        """
        Get tickets by hotel ID

        Args:
            db: Database session
            hotel_id: Hotel ID
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of tickets
        """
        result = await db.execute(
            select(Ticket)
            .filter(Ticket.hotel_id == hotel_id)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self,
        db: AsyncSession,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Ticket]:
        """
        Get tickets by status

        Args:
            db: Database session
            status: Ticket status
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of tickets
        """
        result = await db.execute(
            select(Ticket)
            .filter(Ticket.status == status)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> list[Ticket]:
        """
        Get tickets by conversation ID

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            List of tickets
        """
        result = await db.execute(
            select(Ticket)
            .filter(Ticket.conversation_id == conversation_id)
            .order_by(Ticket.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_relations(
        self,
        db: AsyncSession,
        ticket_id: str,
    ) -> Ticket | None:
        """
        Get ticket with related objects

        Args:
            db: Database session
            ticket_id: Ticket ID

        Returns:
            Ticket with relations or None
        """
        result = await db.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.hotel),
                selectinload(Ticket.conversation),
                selectinload(Ticket.assignee),
                selectinload(Ticket.timelines),
            )
            .filter(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_open_tickets(
        self,
        db: AsyncSession,
        hotel_id: str | None = None,
        limit: int = 100,
    ) -> list[Ticket]:
        """
        Get open (not resolved/closed) tickets

        Args:
            db: Database session
            hotel_id: Filter by hotel ID
            limit: Maximum records to return

        Returns:
            List of open tickets
        """
        conditions = [
            or_(
                Ticket.status == TicketStatus.PENDING.value,
                Ticket.status == TicketStatus.ASSIGNED.value,
                Ticket.status == TicketStatus.IN_PROGRESS.value,
            )
        ]

        if hotel_id:
            conditions.append(Ticket.hotel_id == hotel_id)

        result = await db.execute(
            select(Ticket)
            .filter(and_(*conditions))
            .order_by(Ticket.priority.asc(), Ticket.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_overdue_tickets(
        self,
        db: AsyncSession,
        hotel_id: str | None = None,
    ) -> list[Ticket]:
        """
        Get overdue tickets

        Args:
            db: Database session
            hotel_id: Filter by hotel ID

        Returns:
            List of overdue tickets
        """
        from datetime import datetime
        from sqlalchemy import and_

        conditions = [
            Ticket.due_at < datetime.utcnow(),
            Ticket.status.in_([
                TicketStatus.PENDING.value,
                TicketStatus.ASSIGNED.value,
                TicketStatus.IN_PROGRESS.value,
            ])
        ]

        if hotel_id:
            conditions.append(Ticket.hotel_id == hotel_id)

        result = await db.execute(
            select(Ticket)
            .filter(and_(*conditions))
            .order_by(Ticket.due_at.asc())
        )
        return list(result.scalars().all())


# Create singleton instance
ticket = CRUDTicket(Ticket)
