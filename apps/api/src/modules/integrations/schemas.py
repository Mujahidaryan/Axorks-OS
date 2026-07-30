"""Axorks OS — Integrations Schemas"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class IntegrationConnect(BaseModel):
    provider: str
    category: str | None = None
    access_token: str
    refresh_token: str | None = None
    account_identifier: str | None = None
    scopes: list[str] | None = None


class IntegrationRead(BaseModel):
    id: UUID
    organization_id: UUID
    provider: str
    category: str | None = None
    status: str
    account_identifier: str | None = None
    scopes: list[str] | None = None
    connected_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookCreate(BaseModel):
    integration_id: UUID | None = None
    url: str
    secret: str | None = None
    events: list[str] = ["lead.created", "deal.won"]


class WebhookRead(BaseModel):
    id: UUID
    organization_id: UUID
    integration_id: UUID | None = None
    url: str
    events: list[str] | None = None
    is_active: bool
    last_triggered_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}