"""005_proposal_generator

Revision ID: 005_proposal_generator
Revises: 004_ai_sales_assistant
Create Date: 2026-07-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '005_proposal_generator'
down_revision: Union[str, None] = '004_ai_sales_assistant'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # proposals
    op.create_table(
        'proposals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deal_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('type', sa.String(50), server_default='proposal'),  # proposal, quotation, sow, contract, technical_proposal
        sa.Column('status', sa.String(50), server_default='draft'),  # draft, sent, accepted, rejected
        sa.Column('content', postgresql.JSONB(), server_default='{}', nullable=False),
        sa.Column('total_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('accepted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('pdf_url', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index('idx_proposals_org_ws', 'proposals', ['organization_id', 'workspace_id'])

    # proposal_milestones
    op.create_table(
        'proposal_milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('proposal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('proposals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
    )
    op.create_index('idx_proposal_milestones_proposal', 'proposal_milestones', ['proposal_id'])

    # proposal_templates
    op.create_table(
        'proposal_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('default_content', postgresql.JSONB(), server_default='{}', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # proposal_versions
    op.create_table(
        'proposal_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('proposal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('proposals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('snapshot', postgresql.JSONB(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('proposal_versions')
    op.drop_table('proposal_templates')
    op.drop_table('proposal_milestones')
    op.drop_table('proposals')
