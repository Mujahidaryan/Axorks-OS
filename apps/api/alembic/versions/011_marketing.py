"""011_marketing

Revision ID: 011_marketing
Revises: 010_knowledge_base
Create Date: 2026-07-30

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '011_marketing'
down_revision: Union[str, None] = '010_knowledge_base'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # marketing_campaigns
    op.create_table(
        'marketing_campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('type', sa.String(50), server_default='email'),  # email, social, ads, seo, content
        sa.Column('status', sa.String(50), server_default='draft'),  # draft, active, paused, completed
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('budget', sa.Numeric(15, 2), nullable=True),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('metrics', postgresql.JSONB(), nullable=True),  # impressions, clicks, conversions, leads
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index('idx_campaigns_org', 'marketing_campaigns', ['organization_id'])

    # content_calendar
    op.create_table(
        'content_calendar',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('marketing_campaigns.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content_type', sa.String(50), server_default='post'),  # post, email, blog, video, reel
        sa.Column('platform', sa.String(50), nullable=True),  # linkedin, twitter, instagram, newsletter
        sa.Column('scheduled_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), server_default='draft'),  # draft, scheduled, published, archived
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_content_org', 'content_calendar', ['organization_id'])

    # email_campaigns
    op.create_table(
        'email_campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('marketing_campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('from_name', sa.String(255), nullable=True),
        sa.Column('html_body', sa.Text(), nullable=True),
        sa.Column('text_body', sa.Text(), nullable=True),
        sa.Column('recipient_count', sa.Integer(), server_default='0'),
        sa.Column('sent_count', sa.Integer(), server_default='0'),
        sa.Column('open_count', sa.Integer(), server_default='0'),
        sa.Column('click_count', sa.Integer(), server_default='0'),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('email_campaigns')
    op.drop_table('content_calendar')
    op.drop_table('marketing_campaigns')
