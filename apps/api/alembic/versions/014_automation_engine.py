"""014_automation_engine

Revision ID: 014_automation_engine
Revises: 013_hr
Create Date: 2026-07-30

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '014_automation_engine'
down_revision: Union[str, None] = '013_hr'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # workflows
    op.create_table(
        'workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('trigger_type', sa.String(100), nullable=False),  # entity_event, schedule
        sa.Column('trigger_config', postgresql.JSONB(), nullable=True),  # {"entity": "lead", "event": "created"}
        sa.Column('conditions', postgresql.JSONB(), nullable=True),   # [{"field": "score", "op": "gt", "value": 70}]
        sa.Column('actions', postgresql.JSONB(), nullable=True),       # [{"type": "assign", "data": {...}}]
        sa.Column('run_count', sa.Integer(), server_default='0'),
        sa.Column('last_run_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_workflows_org', 'workflows', ['organization_id'])

    # workflow_executions
    op.create_table(
        'workflow_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('trigger_entity_type', sa.String(100), nullable=True),
        sa.Column('trigger_entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), server_default='running'),  # running, success, failed, skipped
        sa.Column('steps_log', postgresql.JSONB(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index('idx_executions_workflow', 'workflow_executions', ['workflow_id'])


def downgrade() -> None:
    op.drop_table('workflow_executions')
    op.drop_table('workflows')
