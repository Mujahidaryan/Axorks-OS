"""
Axorks OS — Contact Pydantic Schemas
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ContactCreate(BaseModel):
    company_id: UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    linkedin_url: str | None = None
    is_primary: bool = False
    owner_id: UUID | None = None
    tags: list[str] = []


class ContactUpdate(BaseModel):
    company_id: UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    linkedin_url: str | None = None
    is_primary: bool | None = None
    owner_id: UUID | None = None
    tags: list[str] | None = None


class ContactRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    company_id: UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    linkedin_url: str | None = None
    is_primary: bool = False
    owner_id: UUID | None = None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
