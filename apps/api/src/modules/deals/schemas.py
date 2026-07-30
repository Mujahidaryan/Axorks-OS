"""
Axorks OS — Deal Pydantic Schemas
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class DealCreate(BaseModel):
    company_id: UUID | None = None
    contact_id: UUID | None = None
    lead_id: UUID | None = None
    title: str
    value: Decimal | None = None
    currency: str = "USD"
    status: str = "open"
    stage: str | None = None
    probability: int | None = None
    expected_close: date | None = None
    owner_id: UUID | None = None


class DealUpdate(BaseModel):
    company_id: UUID | None = None
    contact_id: UUID | None = None
    title: str | None = None
    value: Decimal | None = None
    currency: str | None = None
    status: str | None = None
    stage: str | None = None
    probability: int | None = None
    expected_close: date | None = None
    owner_id: UUID | None = None
    lost_reason: str | None = None


class DealRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    company_id: UUID | None = None
    contact_id: UUID | None = None
    lead_id: UUID | None = None
    title: str
    value: Decimal | None = None
    currency: str = "USD"
    status: str
    stage: str | None = None
    probability: int | None = None
    expected_close: date | None = None
    owner_id: UUID | None = None
    won_at: datetime | None = None
    lost_at: datetime | None = None
    lost_reason: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
