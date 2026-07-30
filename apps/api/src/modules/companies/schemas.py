"""
Axorks OS — Company Pydantic Schemas
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    website: str | None = None
    industry: str | None = None
    country: str | None = None
    size: str | None = None
    revenue_range: str | None = None
    linkedin_url: str | None = None
    logo_url: str | None = None
    owner_id: UUID | None = None
    tags: list[str] = []
    custom_fields: dict = {}


class CompanyUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    industry: str | None = None
    country: str | None = None
    size: str | None = None
    revenue_range: str | None = None
    linkedin_url: str | None = None
    logo_url: str | None = None
    owner_id: UUID | None = None
    tags: list[str] | None = None
    custom_fields: dict | None = None


class CompanyRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    name: str
    website: str | None = None
    industry: str | None = None
    country: str | None = None
    size: str | None = None
    revenue_range: str | None = None
    linkedin_url: str | None = None
    logo_url: str | None = None
    lead_id: UUID | None = None
    owner_id: UUID | None = None
    tags: list[str] = []
    custom_fields: dict = {}
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
