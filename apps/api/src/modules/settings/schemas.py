"""
Axorks OS — Settings Pydantic Schemas
"""

from pydantic import BaseModel


class OrgSettingsUpdate(BaseModel):
    """Update organization settings (JSONB)."""
    theme: str | None = None
    currency: str | None = None
    timezone: str | None = None
    date_format: str | None = None


class WorkspaceSettingsUpdate(BaseModel):
    """Update workspace settings (JSONB)."""
    default_assignee_id: str | None = None
    auto_archive_days: int | None = None
