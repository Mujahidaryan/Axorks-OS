"""
Axorks OS — Workspace Pydantic Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    """Create workspace request."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")


class WorkspaceRead(BaseModel):
    """Workspace response."""
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    is_default: bool = False
    settings: dict = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceUpdate(BaseModel):
    """Update workspace request."""
    name: str | None = None
    slug: str | None = None
    settings: dict | None = None


class WorkspaceMemberRead(BaseModel):
    """Workspace member response."""
    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
