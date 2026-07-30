"""
Axorks OS — Client Portal Schemas
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class PortalLoginRequest(BaseModel):
    email: str
    password: str


class PortalUserRead(BaseModel):
    id: UUID
    organization_id: UUID
    company_id: UUID
    email: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketMessageCreate(BaseModel):
    message: str


class TicketMessageRead(BaseModel):
    id: UUID
    ticket_id: UUID
    sender_type: str
    sender_name: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SupportTicketCreate(BaseModel):
    subject: str
    description: str
    priority: str = "medium"


class SupportTicketRead(BaseModel):
    id: UUID
    company_id: UUID
    portal_user_id: UUID
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime

    model_config = {"from_attributes": True}
