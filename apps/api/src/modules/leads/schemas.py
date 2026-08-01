"""
Axorks OS — Lead Pydantic Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from src.modules.leads.models import LeadSource, LeadStatus


class LeadCreate(BaseModel):
    """Create lead request — ALL fields optional except organization context!"""
    business_name: str | None = None
    website: str | None = None
    industry: str | None = None
    country: str | None = None
    company_size: str | None = None
    revenue_range: str | None = None
    linkedin_url: str | None = None

    decision_maker_name: str | None = None
    decision_maker_title: str | None = None
    phone: str | None = None
    email: EmailStr | str | None = None

    source: LeadSource = LeadSource.MANUAL
    source_detail: str | None = None
    status: LeadStatus = LeadStatus.NEW
    score: int = 0
    owner_id: UUID | None = None
    notes: str | None = None
    tags: list[str] = []
    custom_fields: dict = {}


class LeadUpdate(BaseModel):
    """Update lead request — all fields optional."""
    business_name: str | None = None
    website: str | None = None
    industry: str | None = None
    country: str | None = None
    company_size: str | None = None
    revenue_range: str | None = None
    linkedin_url: str | None = None

    decision_maker_name: str | None = None
    decision_maker_title: str | None = None
    phone: str | None = None
    email: str | None = None

    source: LeadSource | None = None
    source_detail: str | None = None
    status: LeadStatus | None = None
    score: int | None = None
    owner_id: UUID | None = None
    notes: str | None = None
    tags: list[str] | None = None
    custom_fields: dict | None = None


class LeadRead(BaseModel):
    """Lead response model."""
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    business_name: str | None = None
    website: str | None = None
    industry: str | None = None
    country: str | None = None
    company_size: str | None = None
    revenue_range: str | None = None
    linkedin_url: str | None = None

    decision_maker_name: str | None = None
    decision_maker_title: str | None = None
    phone: str | None = None
    email: str | None = None

    source: LeadSource
    source_detail: str | None = None
    status: LeadStatus
    score: int
    owner_id: UUID | None = None
    notes: str | None = None
    tags: list[str] = []
    custom_fields: dict = {}
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BulkAssignRequest(BaseModel):
    lead_ids: list[UUID]
    owner_id: UUID


class BulkStatusRequest(BaseModel):
    lead_ids: list[UUID]
    status: LeadStatus


class BulkTagRequest(BaseModel):
    lead_ids: list[UUID]
    add_tags: list[str] = []
    remove_tags: list[str] = []


class ScoreLeadRequest(BaseModel):
    score: int | None = None  # If None, AI auto-score
    reason: str | None = None


class CSVImportMappingRequest(BaseModel):
    filename: str
    column_mapping: dict[str, str]  # csv_col -> lead_field
    csv_rows: list[dict[str, str]]


class PublicLeadCaptureRequest(BaseModel):
    """Zero-cost public website / form / webhook lead capture schema."""
    workspace_id: UUID | None = None
    organization_id: UUID | None = None
    business_name: str | None = None
    decision_maker_name: str | None = None
    decision_maker_title: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    industry: str | None = None
    country: str | None = None
    company_size: str | None = None
    source: LeadSource = LeadSource.WEBSITE
    source_detail: str | None = None
    notes: str | None = None
    tags: list[str] = []
    custom_fields: dict = {}

