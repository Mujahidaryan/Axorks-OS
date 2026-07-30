"""
Axorks OS — AI Provider & Sales Assistant Pydantic / SQLAlchemy Models
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, Field
from sqlalchemy import TIMESTAMP, UUID, BigInteger, Boolean, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.base_model import Base


# ── SQLAlchemy Models ────────────────────────────────────────

class AIPrompt(Base):
    __tablename__ = "ai_prompts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    variables: Mapped[dict] = mapped_column(JSONB, default=list)
    model_config_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AIActionConfirmation(Base):
    __tablename__ = "ai_action_confirmations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    proposed_changes: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    confirmed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    task_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tokens_input: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_output: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


# ── Pydantic Schemas ──────────────────────────────────────────

class AIConfig(BaseModel):
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    provider: str | None = None


class AIResponse(BaseModel):
    content: str
    model: str
    provider: str
    tokens_input: int = 0
    tokens_output: int = 0
    finish_reason: str = "stop"


class AIContext(BaseModel):
    organization_id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    entity_snapshot: dict[str, Any] | None = None
    task_type: str = "sales_assistant"


class AISuggestQuestionsRequest(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    context_text: str | None = None


class AISummarizeRequest(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    text_content: str | None = None


class AIDetectRequirementsRequest(BaseModel):
    conversation_text: str


class AIEstimateBudgetRequest(BaseModel):
    requirements: list[str]
    industry: str | None = None


class AIEstimateComplexityRequest(BaseModel):
    requirements: list[str]


class AISuggestTechRequest(BaseModel):
    requirements: list[str]
    preferences: list[str] = []


class AISuggestFollowupRequest(BaseModel):
    call_outcome: str
    key_points: list[str] = []


class AIDetectObjectionsRequest(BaseModel):
    transcript_text: str


class AIActionItemsRequest(BaseModel):
    conversation_text: str


class AIUpdateCRMRequest(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    text_source: str


class AIActionConfirmationRead(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    action_type: str
    proposed_changes: dict
    reasoning: str | None = None
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}
