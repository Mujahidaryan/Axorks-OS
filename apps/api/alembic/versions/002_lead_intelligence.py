"""002_lead_intelligence

Revision ID: 002_lead_intelligence
Revises: 001_foundation
Create Date: 2026-07-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002_lead_intelligence'
down_revision: Union[str, None] = '001_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enum Types
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE lead_status AS ENUM (
                'new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost', 'archived'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE lead_source AS ENUM (
                'linkedin', 'instagram', 'facebook', 'youtube', 'website',
                'cold_call', 'cold_email', 'referral', 'manual', 'csv', 'api',
                'google_business', 'directory', 'other'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Leads Table
    op.create_table(
        'leads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id'), nullable=False),

        # Business Info
        sa.Column('business_name', sa.String(500), nullable=True),
        sa.Column('website', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(200), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('company_size', sa.String(50), nullable=True),
        sa.Column('revenue_range', sa.String(50), nullable=True),
        sa.Column('linkedin_url', sa.Text(), nullable=True),

        # Decision Maker
        sa.Column('decision_maker_name', sa.String(255), nullable=True),
        sa.Column('decision_maker_title', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),

        # CRM Fields
        sa.Column('source', postgresql.ENUM('linkedin', 'instagram', 'facebook', 'youtube', 'website', 'cold_call', 'cold_email', 'referral', 'manual', 'csv', 'api', 'google_business', 'directory', 'other', name='lead_source', create_type=False), server_default='manual'),
        sa.Column('source_detail', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost', 'archived', name='lead_status', create_type=False), server_default='new'),
        sa.Column('score', sa.Integer(), server_default='0'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), server_default='{}'),
        sa.Column('custom_fields', postgresql.JSONB(), server_default='{}'),

        # Metadata
        sa.Column('version', sa.Integer(), server_default='1'),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )

    # Indexes
    op.create_index('idx_leads_org_ws', 'leads', ['organization_id', 'workspace_id'])
    op.create_index('idx_leads_status', 'leads', ['organization_id', 'status'])
    op.create_index('idx_leads_owner', 'leads', ['organization_id', 'owner_id'])
    op.create_index('idx_leads_score', 'leads', ['organization_id', 'score'])
    op.create_index('idx_leads_tags', 'leads', ['tags'], postgresql_using='gin')
    op.create_index('idx_leads_search', 'leads', ['search_vector'], postgresql_using='gin')

    # Lead Score History Table
    op.create_table(
        'lead_score_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leads.id'), nullable=False),
        sa.Column('old_score', sa.Integer(), nullable=True),
        sa.Column('new_score', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('scored_by', sa.String(50), nullable=True), # 'manual' | 'ai' | 'automation'
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Lead Imports Table
    op.create_table(
        'lead_imports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(500), nullable=True),
        sa.Column('total_rows', sa.Integer(), nullable=True),
        sa.Column('imported_rows', sa.Integer(), server_default='0'),
        sa.Column('failed_rows', sa.Integer(), server_default='0'),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('error_log', postgresql.JSONB(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('lead_imports')
    op.drop_table('lead_score_history')
    op.drop_table('leads')
    op.execute("DROP TYPE IF EXISTS lead_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS lead_source CASCADE;")
