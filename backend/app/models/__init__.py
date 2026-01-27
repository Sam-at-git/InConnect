"""SQLAlchemy ORM models"""

from app.core.database import Base
from app.models.hotel import Hotel
from app.models.staff import Staff, StaffRole, StaffStatus
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, MessageType, MessageDirection
from app.models.ticket import (
    Ticket,
    TicketStatus,
    TicketPriority,
    TicketCategory,
)
from app.models.routing_rule import RoutingRule, RoutingRuleType, RoutingRuleStatus
from app.models.ticket_timeline import TicketTimeline, TimelineEventType
from app.models.auto_rule import AutoTicketRule, TriggerType, AutoTicketRuleStatus
from app.models.sla_config import SLAConfig
from app.models.system_config import SystemConfig

__all__ = [
    "Base",
    "Hotel",
    "Staff",
    "StaffRole",
    "StaffStatus",
    "Conversation",
    "ConversationStatus",
    "Message",
    "MessageType",
    "MessageDirection",
    "Ticket",
    "TicketStatus",
    "TicketPriority",
    "TicketCategory",
    "RoutingRule",
    "RoutingRuleType",
    "RoutingRuleStatus",
    "TicketTimeline",
    "TimelineEventType",
    "AutoTicketRule",
    "TriggerType",
    "AutoTicketRuleStatus",
    "SLAConfig",
    "SystemConfig",
]
