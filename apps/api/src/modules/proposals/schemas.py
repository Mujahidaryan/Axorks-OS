"""
Axorks OS — Proposal Schemas
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ProposalMilestoneSchema(BaseModel):
    id: UUID | None = None
    title: str
    description: str | None = None
    amount: Decimal | None = None
    due_date: date | None = None
    sort_order: int = 0


class TimelineMilestoneSchema(BaseModel):
    title: str
    description: str | None = None
    duration: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    deliverables: str | None = None


class PaymentMilestoneSchema(BaseModel):
    title: str
    amount: Decimal | None = None
    due_date: date | None = None
    percentage: int | None = None


class ProposalCreate(BaseModel):
    deal_id: UUID | None = None
    company_id: UUID | None = None
    title: str
    type: str = "proposal"
    content: dict = Field(default_factory=dict)
    total_value: Decimal | None = None
    currency: str = "USD"
    valid_until: date | None = None
    milestones: list[ProposalMilestoneSchema] = Field(default_factory=list)


class ProposalGenerateRequest(BaseModel):
    deal_id: UUID | None = None
    company_id: UUID | None = None
    proposal_type: str = "proposal"
    template_id: UUID | None = None
    additional_notes: str | None = None


class ProposalUpdate(BaseModel):
    title: str | None = None
    type: str | None = None
    status: str | None = None
    content: dict | None = None
    total_value: Decimal | None = None
    currency: str | None = None
    valid_until: date | None = None
    milestones: list[ProposalMilestoneSchema] | None = None


class ProposalSendRequest(BaseModel):
    recipient_email: str | None = None
    subject: str | None = None
    message: str | None = None


class ProposalImproveSectionRequest(BaseModel):
    section_index: int = Field(ge=0)
    instruction: str | None = None


class ProposalRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    deal_id: UUID | None = None
    company_id: UUID | None = None
    title: str
    type: str
    status: str
    content: dict
    total_value: Decimal | None = None
    currency: str
    valid_until: date | None = None
    sent_at: datetime | None = None
    accepted_at: datetime | None = None
    pdf_url: str | None = None
    version: int
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    milestones: list[ProposalMilestoneSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ProposalVersionRead(BaseModel):
    id: UUID
    proposal_id: UUID
    version: int
    snapshot: dict
    created_by: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProposalTemplateCreate(BaseModel):
    name: str
    type: str
    default_content: dict = Field(default_factory=dict)


class ProposalTemplateUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    default_content: dict | None = None


class ProposalTemplateRead(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    type: str
    default_content: dict
    created_at: datetime

    model_config = {"from_attributes": True}
