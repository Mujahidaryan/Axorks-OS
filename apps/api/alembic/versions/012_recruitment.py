"""012_recruitment

Revision ID: 012_recruitment
Revises: 011_marketing
Create Date: 2026-07-30

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '012_recruitment'
down_revision: Union[str, None] = '011_marketing'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # job_openings
    op.create_table(
        'job_openings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('department', sa.String(255), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('employment_type', sa.String(50), server_default='full_time'),  # full_time, part_time, contract, remote
        sa.Column('status', sa.String(50), server_default='open'),  # open, paused, closed, filled
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('salary_min', sa.Numeric(15, 2), nullable=True),
        sa.Column('salary_max', sa.Numeric(15, 2), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # candidates
    op.create_table(
        'candidates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_opening_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('job_openings.id', ondelete='SET NULL'), nullable=True),
        sa.Column('full_name', sa.String(500), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('linkedin_url', sa.Text(), nullable=True),
        sa.Column('cv_url', sa.Text(), nullable=True),
        sa.Column('stage', sa.String(50), server_default='applied'),  # applied, screening, interview, offer, hired, rejected
        sa.Column('ai_cv_summary', sa.Text(), nullable=True),
        sa.Column('ai_score', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_candidates_org', 'candidates', ['organization_id'])

    # interviews
    op.create_table(
        'interviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scheduled_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('interview_type', sa.String(50), server_default='video'),  # video, phone, onsite, technical
        sa.Column('interviewer_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),  # 1-5
        sa.Column('outcome', sa.String(50), nullable=True),  # pass, fail, pending
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('interviews')
    op.drop_table('candidates')
    op.drop_table('job_openings')
