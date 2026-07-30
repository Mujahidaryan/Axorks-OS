"""
Axorks OS — User Pydantic Schemas

Request/response DTOs for user profile operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    """User profile response."""
    id: UUID
    email: EmailStr
    email_verified: bool
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    phone: str | None = None
    timezone: str = "UTC"
    locale: str = "en"
    preferences: dict = {}
    two_factor_enabled: bool = False
    last_login_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Update user profile — all fields optional."""
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    timezone: str | None = None
    locale: str | None = None
    avatar_url: str | None = None


class UserPreferencesUpdate(BaseModel):
    """Update user preferences (JSONB merge)."""
    theme: str | None = None  # "light" | "dark" | "system"
    sidebar_collapsed: bool | None = None
    notifications_enabled: bool | None = None
    email_notifications: bool | None = None
