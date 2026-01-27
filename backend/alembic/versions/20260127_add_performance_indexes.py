"""add performance indexes

Revision ID: 20260127_add_perf_indexes
Revises: 20260127_initial_create_all_core_tables
Create Date: 2026-01-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260127_add_perf_indexes'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add composite indexes for tickets table
    op.create_index(
        'ix_tickets_hotel_status',
        'tickets',
        ['hotel_id', 'status']
    )
    op.create_index(
        'ix_tickets_assigned_status',
        'tickets',
        ['assigned_to', 'status']
    )
    op.create_index(
        'ix_tickets_hotel_created',
        'tickets',
        ['hotel_id', 'created_at']
    )

    # Add indexes for messages table
    op.create_index(
        'ix_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at']
    )
    op.create_index(
        'ix_messages_conversation_direction',
        'messages',
        ['conversation_id', 'direction']
    )

    # Add indexes for conversations table
    op.create_index(
        'ix_conversations_hotel_status',
        'conversations',
        ['hotel_id', 'status']
    )

    # Add GIN index for full-text search on message content
    # Note: This requires PostgreSQL with pg_trgm extension
    # op.execute('CREATE INDEX ix_messages_content_trgm ON messages USING gin(content gin_trgm_ops)')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_tickets_hotel_status', table_name='tickets')
    op.drop_index('ix_tickets_assigned_status', table_name='tickets')
    op.drop_index('ix_tickets_hotel_created', table_name='tickets')
    op.drop_index('ix_messages_conversation_created', table_name='messages')
    op.drop_index('ix_messages_conversation_direction', table_name='messages')
    op.drop_index('ix_conversations_hotel_status', table_name='conversations')
