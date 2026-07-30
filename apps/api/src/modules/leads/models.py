"""
Axorks OS — Lead Models

Lead, LeadScoreHistory, and LeadImport ORM definitions.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    UUID,
    Column,
    Enum,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.base_model import Base, TenantModel


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    ARCHIVED = "archived"


class LeadSource(str, enum.Enum):
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    WEBSITE = "website"
    COLD_CALL = "cold_call"
    COLD_EMAIL = "cold_email"
    REFERRAL = "referral"
    MANUAL = "manual"
    CSV = "csv"
    API = "api"
    GOOGLE_BUSINESS = "google_business"
    DIRECTORY = "directory"
    OTHER = "other"


class Lead(TenantModel):
    """Lead entity — the core sales prospect in Axorks OS."""

    __tablename__ = "leads"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    # Business Info
    business_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(200), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    revenue_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Decision Maker
    decision_maker_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision_maker_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # CRM Fields
    source: Mapped[LeadSource] = mapped_column(
        Enum(LeadSource, name="lead_source"), default=LeadSource.MANUAL
    )
    source_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="lead_status"), default=LeadStatus.NEW
    )
    score: Mapped[int] = mapped_column(Integer, default=0)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    custom_fields: Mapped[dict] = mapped_column(JSONB, default=dict)

    version: Mapped[int] = mapped_column(Integer, default=1)
    search_vector: Mapped[Any | None] = mapped_column(TSVECTOR, nullable=True)


class LeadScoreHistory(Base):
    """Historical record of lead quality score changes."""

    __tablename__ = "lead_score_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    old_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_score: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    scored_by: Mapped[str | None] = mapped_column(String(50), default="manual")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class LeadImport(Base):
    """CSV / Bulk import job record."""

    __tablename__ = "lead_imports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_rows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    imported_rows: Mapped[int] = mapped_column(Integer, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_log: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
