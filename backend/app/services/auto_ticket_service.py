"""
Auto-ticket creation service
"""

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auto_rule import AutoTicketRule, TriggerType
from app.models.message import Message
from app.models.conversation import Conversation
from app.models.ticket import Ticket, TicketCategory, TicketPriority, TicketStatus
from app.core.logging import get_logger

logger = get_logger("app.services.auto_ticket_service")


class AutoTicketService:
    """
    Service for automatically creating tickets based on messages
    """

    async def should_create_ticket(
        self,
        db: AsyncSession,
        message: Message,
    ) -> bool:
        """
        Check if a ticket should be created for this message

        Args:
            db: Database session
            message: Incoming message

        Returns:
            True if ticket should be created
        """
        # Get conversation
        conv_result = await db.execute(
            select(Conversation).filter(Conversation.id == message.conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            return False

        # Get active rules for the hotel
        result = await db.execute(
            select(AutoTicketRule)
            .filter(
                AutoTicketRule.hotel_id == conversation.hotel_id,
                AutoTicketRule.is_active == True,  # noqa: E712
            )
            .order_by(AutoTicketRule.priority_level.desc())
        )
        rules = result.scalars().all()

        for rule in rules:
            if await self._matches_trigger(db, message, rule):
                return True

        return False

    async def create_ticket_from_message(
        self,
        db: AsyncSession,
        message: Message,
    ) -> Ticket | None:
        """
        Create a ticket based on message and matching rules

        Args:
            db: Database session
            message: Incoming message

        Returns:
            Created ticket or None
        """
        # Get conversation
        conv_result = await db.execute(
            select(Conversation).filter(Conversation.id == message.conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            return None

        # Get active rules
        result = await db.execute(
            select(AutoTicketRule)
            .filter(
                AutoTicketRule.hotel_id == conversation.hotel_id,
                AutoTicketRule.is_active == True,  # noqa: E712
            )
            .order_by(AutoTicketRule.priority_level.desc())
        )
        rules = result.scalars().all()

        for rule in rules:
            if await self._matches_trigger(db, message, rule):
                return await self._create_ticket(db, message, conversation, rule)

        return None

    async def _matches_trigger(
        self,
        db: AsyncSession,
        message: Message,
        rule: AutoTicketRule,
    ) -> bool:
        """
        Check if message matches rule trigger

        Args:
            db: Database session
            message: Message to check
            rule: Rule to match against

        Returns:
            True if matches
        """
        if rule.trigger_type == TriggerType.KEYWORD.value:
            keywords = json.loads(rule.keywords) if rule.keywords else []
            content = message.content or ""
            return any(kw.lower() in content.lower() for kw in keywords)

        return False

    async def _create_ticket(
        self,
        db: AsyncSession,
        message: Message,
        conversation: Conversation,
        rule: AutoTicketRule,
    ) -> Ticket:
        """
        Create ticket from message and rule

        Args:
            db: Database session
            message: Trigger message
            conversation: Conversation
            rule: Matched rule

        Returns:
            Created ticket
        """
        import uuid
        from datetime import datetime

        # Generate ticket ID
        ticket_id = f"TK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

        # Build title and description
        title = self._render_template(
            rule.ticket_title_template,
            message,
            conversation,
        )
        description = self._render_template(
            rule.ticket_description_template or "",
            message,
            conversation,
        )

        # Create ticket
        ticket = Ticket(
            id=ticket_id,
            hotel_id=conversation.hotel_id,
            conversation_id=conversation.id,
            title=title,
            description=description,
            category=rule.ticket_category,
            priority=rule.ticket_priority,
            status=TicketStatus.PENDING.value,
        )

        db.add(ticket)
        await db.flush()

        # Create timeline entry
        from app.models.ticket_timeline import TicketTimeline
        timeline = TicketTimeline(
            ticket_id=ticket.id,
            staff_id=None,
            event_type="created",
            new_value=title,
            comment=f"Auto-created from message: {message.content[:50]}...",
        )
        db.add(timeline)

        # Auto-assign if enabled
        if rule.auto_assign:
            from app.services.routing_service import routing_service
            assigned = await routing_service.auto_assign_ticket(db, ticket)
            if assigned:
                # Update timeline
                assign_timeline = TicketTimeline(
                    ticket_id=ticket.id,
                    staff_id=None,
                    event_type="assigned",
                    new_value=ticket.assigned_to,
                    comment="Auto-assigned based on routing rules",
                )
                db.add(assign_timeline)

        await db.commit()

        logger.info(
            "Auto-ticket created",
            extra={
                "ticket_id": ticket.id,
                "rule_id": rule.id,
                "message_id": message.id,
            },
        )

        return ticket

    def _render_template(
        self,
        template: str,
        message: Message,
        conversation: Conversation,
    ) -> str:
        """
        Render template with variables

        Args:
            template: Template string
            message: Message data
            conversation: Conversation data

        Returns:
            Rendered string
        """
        variables = {
            "{guest_name}": conversation.guest_name or "客人",
            "{guest_phone}": conversation.guest_phone or "",
            "{message_content}": message.content or "",
            "{hotel_id}": conversation.hotel_id,
        }

        result = template
        for key, value in variables.items():
            result = result.replace(key, value)

        return result


# Create singleton instance
auto_ticket_service = AutoTicketService()
