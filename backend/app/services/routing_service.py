"""
Ticket Assignment and Routing Service
"""

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.routing_rule import RoutingRule, RoutingRuleType
from app.models.staff import Staff, StaffStatus
from app.models.ticket import Ticket
from app.models.message import Message, MessageType
from app.core.logging import get_logger

logger = get_logger("app.services.routing_service")


class RoutingService:
    """
    Service for intelligent ticket assignment based on routing rules
    """

    async def find_assignee_for_ticket(
        self,
        db: AsyncSession,
        ticket: Ticket,
    ) -> str | None:
        """
        Find the best staff member to assign a ticket based on routing rules

        Args:
            db: Database session
            ticket: Ticket to assign

        Returns:
            Staff ID to assign to, or None if no match found
        """
        # Get active routing rules for the hotel, ordered by priority
        result = await db.execute(
            select(RoutingRule)
            .filter(
                RoutingRule.hotel_id == ticket.hotel_id,
                RoutingRule.is_active == True,  # noqa: E712
            )
            .order_by(RoutingRule.priority_level.desc())
        )
        rules = result.scalars().all()

        for rule in rules:
            if await self._matches_rule(db, ticket, rule):
                target_staff_ids = json.loads(rule.target_staff_ids)
                if not target_staff_ids:
                    continue

                # Get available staff from targets
                available_staff = await self._get_available_staff(
                    db, target_staff_ids
                )

                if available_staff:
                    # For MVP, return first available
                    # In production, implement round-robin or load balancing
                    return available_staff[0].id

        return None

    async def find_assignee_for_message(
        self,
        db: AsyncSession,
        message: Message,
    ) -> str | None:
        """
        Find assignee based on incoming message

        Args:
            db: Database session
            message: Incoming message

        Returns:
            Staff ID to assign to, or None
        """
        # Get conversation to find hotel
        from app.models.conversation import Conversation

        conv_result = await db.execute(
            select(Conversation).filter(Conversation.id == message.conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            return None

        # Get routing rules
        result = await db.execute(
            select(RoutingRule)
            .filter(
                RoutingRule.hotel_id == conversation.hotel_id,
                RoutingRule.is_active == True,  # noqa: E712
            )
            .order_by(RoutingRule.priority_level.desc())
        )
        rules = result.scalars().all()

        for rule in rules:
            if await self._matches_message_rule(db, message, rule):
                target_staff_ids = json.loads(rule.target_staff_ids)
                available_staff = await self._get_available_staff(
                    db, target_staff_ids
                )

                if available_staff:
                    return available_staff[0].id

        return None

    async def _matches_rule(
        self,
        db: AsyncSession,
        ticket: Ticket,
        rule: RoutingRule,
    ) -> bool:
        """
        Check if ticket matches routing rule

        Args:
            db: Database session
            ticket: Ticket to check
            rule: Routing rule

        Returns:
            True if ticket matches rule
        """
        if rule.rule_type == RoutingRuleType.CATEGORY.value:
            return ticket.category == rule.category

        elif rule.rule_type == RoutingRuleType.PRIORITY.value:
            return ticket.priority == rule.priority

        elif rule.rule_type == RoutingRuleType.KEYWORD.value:
            # Check if keywords match ticket title or description
            keywords = json.loads(rule.keywords) if rule.keywords else []
            text = (ticket.title or "") + " " + (ticket.description or "")
            return any(keyword.lower() in text.lower() for keyword in keywords)

        return False

    async def _matches_message_rule(
        self,
        db: AsyncSession,
        message: Message,
        rule: RoutingRule,
    ) -> bool:
        """
        Check if message matches routing rule

        Args:
            db: Database session
            message: Message to check
            rule: Routing rule

        Returns:
            True if message matches rule
        """
        if rule.rule_type == RoutingRuleType.KEYWORD.value:
            keywords = json.loads(rule.keywords) if rule.keywords else []
            content = message.content or ""
            return any(keyword.lower() in content.lower() for keyword in keywords)

        return False

    async def _get_available_staff(
        self,
        db: AsyncSession,
        staff_ids: list[str],
    ) -> list[Staff]:
        """
        Get available staff from list of IDs

        Args:
            db: Database session
            staff_ids: List of staff IDs to check

        Returns:
            List of available staff
        """
        result = await db.execute(
            select(Staff).filter(
                Staff.id.in_(staff_ids),
                Staff.status == StaffStatus.ACTIVE.value,
                Staff.is_available == True,  # noqa: E712
            )
        )
        return list(result.scalars().all())

    async def auto_assign_ticket(
        self,
        db: AsyncSession,
        ticket: Ticket,
    ) -> bool:
        """
        Automatically assign ticket to best matching staff

        Args:
            db: Database session
            ticket: Ticket to assign

        Returns:
            True if assignment was successful
        """
        if ticket.assigned_to:
            logger.info("Ticket already assigned", extra={"ticket_id": ticket.id})
            return False

        assignee_id = await self.find_assignee_for_ticket(db, ticket)
        if assignee_id:
            from app.models.ticket import TicketStatus

            ticket.assigned_to = assignee_id
            ticket.status = TicketStatus.ASSIGNED.value
            await db.flush()

            logger.info(
                "Ticket auto-assigned",
                extra={
                    "ticket_id": ticket.id,
                    "assignee_id": assignee_id,
                },
            )

            return True

        return False


# Create singleton instance
routing_service = RoutingService()
