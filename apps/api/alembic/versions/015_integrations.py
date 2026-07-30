"""015_integrations

Revision ID: 015_integrations
Revises: 014_automation_engine
Create Date: 2026-07-30

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '015_integrations'
down_revision: Union[str, None] = '014_automation_engine'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # integrations
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(100), nullable=False),  # github, google, slack, stripe, resend, openai, etc.
        sa.Column('category', sa.String(50), nullable=True),   # vcs, communication, payment, ai, analytics, social
        sa.Column('status', sa.String(50), server_default='disconnected'),  # connected, disconnected, error
        sa.Column('access_token_encrypted', sa.Text(), nullable=True),
        sa.Column('refresh_token_encrypted', sa.Text(), nullable=True),
        sa.Column('account_identifier', sa.String(255), nullable=True),
        sa.Column('scopes', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('connected_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_integrations_org_provider', 'integrations', ['organization_id', 'provider'], unique=True)

    # webhooks
    op.create_table(
        'webhooks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('integration_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('integrations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('secret', sa.Text(), nullable=True),
        sa.Column('events', postgresql.ARRAY(sa.String()), nullable=True),  # ["lead.created", "deal.won"]
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_triggered_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('webhooks')
    op.drop_table('integrations')
