"""
Axorks OS — Organization Pydantic Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OrgCreate(BaseModel):
    """Create a new organization."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")


class OrgRead(BaseModel):
    """Organization response."""
    id: UUID
    name: str
    slug: str
    logo_url: str | None = None
    plan: str = "free"
    settings: dict = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class OrgUpdate(BaseModel):
    """Update organization — all fields optional."""
    name: str | None = None
    slug: str | None = None
    logo_url: str | None = None
    settings: dict | None = None


class OrgMemberRead(BaseModel):
    """Organization member response."""
    id: UUID
    user_id: UUID
    role: str
    joined_at: datetime | None = None

    model_config = {"from_attributes": True}


class InviteMemberRequest(BaseModel):
    """Invite a user to the organization."""
    email: str
    role: str = "member"
