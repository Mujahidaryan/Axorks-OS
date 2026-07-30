"""004_ai_sales_assistant

Revision ID: 004_ai_sales_assistant
Revises: 003_one_page_crm
Create Date: 2026-07-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004_ai_sales_assistant'
down_revision: Union[str, None] = '003_one_page_crm'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ai_prompts
    op.create_table(
        'ai_prompts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('task_type', sa.String(100), nullable=False),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('user_template', sa.Text(), nullable=True),
        sa.Column('variables', postgresql.JSONB(), server_default='[]'),
        sa.Column('model_config', postgresql.JSONB(), server_default='{}'),
        sa.Column('version', sa.Integer(), server_default='1'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_ai_prompts_task', 'ai_prompts', ['task_type'])

    # ai_action_confirmations
    op.create_table(
        'ai_action_confirmations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', sa.String(100), nullable=False),  # update_crm, create_task, send_email, etc.
        sa.Column('proposed_changes', postgresql.JSONB(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), server_default='pending'),  # pending, confirmed, rejected
        sa.Column('confirmed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('rejected_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_ai_actions_entity', 'ai_action_confirmations', ['entity_type', 'entity_id'])

    # ai_usage_logs
    op.create_table(
        'ai_usage_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_type', sa.String(100), nullable=True),
        sa.Column('provider', sa.String(50), nullable=True),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('tokens_input', sa.Integer(), nullable=True),
        sa.Column('tokens_output', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Numeric(10, 6), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_ai_usage_org', 'ai_usage_logs', ['organization_id'])


def downgrade() -> None:
    op.drop_table('ai_usage_logs')
    op.drop_table('ai_action_confirmations')
    op.drop_table('ai_prompts')
