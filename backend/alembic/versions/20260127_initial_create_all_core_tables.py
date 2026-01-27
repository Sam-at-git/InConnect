"""Initial migration: create all core tables

Revision ID: 001
Revises:
Create Date: 2026-01-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create hotels table
    op.create_table(
        "hotels",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("corp_id", sa.String(100), unique=True, nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("contact_person", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_hotels_id", "hotels", ["id"])

    # Create staff table
    op.create_table(
        "staff",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("hotel_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("wechat_userid", sa.String(100), unique=True, nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("role", sa.String(20), server_default="other"),
        sa.Column("department", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("is_available", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_staff_id", "staff", ["id"])
    op.create_index("ix_staff_hotel_id", "staff", ["hotel_id"])
    op.create_index("ix_staff_wechat_userid", "staff", ["wechat_userid"])

    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("hotel_id", sa.String(36), nullable=False),
        sa.Column("guest_id", sa.String(100), nullable=False),
        sa.Column("guest_name", sa.String(50), nullable=True),
        sa.Column("guest_phone", sa.String(20), nullable=True),
        sa.Column("guest_avatar", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("last_message_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_conversations_id", "conversations", ["id"])
    op.create_index("ix_conversations_hotel_id", "conversations", ["hotel_id"])
    op.create_index("ix_conversations_guest_id", "conversations", ["guest_id"])

    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), nullable=False),
        sa.Column("message_type", sa.String(20), server_default="text"),
        sa.Column("direction", sa.String(20), server_default="inbound"),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("media_url", sa.Text(), nullable=True),
        sa.Column("sender_id", sa.String(100), nullable=True),
        sa.Column("wechat_msg_id", sa.String(100), unique=True, nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default="false"),
        sa.Column("sent_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_messages_id", "messages", ["id"])
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    # Create tickets table
    op.create_table(
        "tickets",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("hotel_id", sa.String(36), nullable=False),
        sa.Column("conversation_id", sa.String(36), nullable=True),
        sa.Column("assigned_to", sa.String(36), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(20), server_default="other"),
        sa.Column("priority", sa.String(10), server_default="P3"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assigned_to"], ["staff.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_tickets_id", "tickets", ["id"])
    op.create_index("ix_tickets_hotel_id", "tickets", ["hotel_id"])
    op.create_index("ix_tickets_status", "tickets", ["status"])
    op.create_index("ix_tickets_created_at", "tickets", ["created_at"])

    # Create routing_rules table
    op.create_table(
        "routing_rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("hotel_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("rule_type", sa.String(20), server_default="keyword"),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("priority", sa.String(10), nullable=True),
        sa.Column("target_staff_ids", sa.Text(), nullable=False),
        sa.Column("priority_level", sa.Integer(), server_default="0"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_routing_rules_id", "routing_rules", ["id"])
    op.create_index("ix_routing_rules_hotel_id", "routing_rules", ["hotel_id"])

    # Create ticket_timeline table
    op.create_table(
        "ticket_timeline",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.String(50), nullable=False),
        sa.Column("staff_id", sa.String(36), nullable=True),
        sa.Column("event_type", sa.String(20), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["staff_id"], ["staff.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_ticket_timeline_id", "ticket_timeline", ["id"])
    op.create_index("ix_ticket_timeline_ticket_id", "ticket_timeline", ["ticket_id"])


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_table("ticket_timeline")
    op.drop_table("routing_rules")
    op.drop_table("tickets")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("staff")
    op.drop_table("hotels")
