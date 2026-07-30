"""Axorks OS — Marketing Schemas"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class CampaignCreate(BaseModel):
    name: str
    type: str = "email"
    start_date: date | None = None
    end_date: date | None = None
    budget: Decimal | None = None
    goal: str | None = None


class CampaignRead(BaseModel):
    id: UUID; organization_id: UUID; workspace_id: UUID; name: str; type: str; status: str
    start_date: date | None = None; end_date: date | None = None; budget: Decimal | None = None
    goal: str | None = None; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class ContentItemCreate(BaseModel):
    title: str; content_type: str = "post"; platform: str | None = None
    scheduled_at: datetime | None = None; body: str | None = None; campaign_id: UUID | None = None


class ContentItemRead(BaseModel):
    id: UUID; organization_id: UUID; campaign_id: UUID | None = None; title: str
    content_type: str; platform: str | None = None; scheduled_at: datetime | None = None
    status: str; body: str | None = None; created_at: datetime
    model_config = {"from_attributes": True}


class EmailCampaignCreate(BaseModel):
    campaign_id: UUID; subject: str; from_name: str | None = None
    html_body: str | None = None; text_body: str | None = None


class EmailCampaignRead(BaseModel):
    id: UUID; organization_id: UUID; campaign_id: UUID; subject: str; from_name: str | None = None
    recipient_count: int; sent_count: int; open_count: int; click_count: int
    sent_at: datetime | None = None; created_at: datetime
    model_config = {"from_attributes": True}
