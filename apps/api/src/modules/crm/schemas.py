"""
Axorks OS — CRM Resource Schemas
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class NoteCreate(BaseModel):
    entity_type: str
    entity_id: UUID
    content: str
    is_pinned: bool = False


class NoteRead(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    content: str
    is_pinned: bool
    created_by: UUID | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class CallCreate(BaseModel):
    entity_type: str
    entity_id: UUID
    direction: str | None = "outbound"
    duration_seconds: int | None = None
    outcome: str | None = None
    recording_url: str | None = None
    called_at: datetime


class CallRead(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    direction: str | None = None
    duration_seconds: int | None = None
    outcome: str | None = None
    recording_url: str | None = None
    called_at: datetime
    created_by: UUID | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class EmailCreate(BaseModel):
    entity_type: str
    entity_id: UUID
    direction: str | None = "outbound"
    subject: str | None = None
    body_text: str | None = None
    from_address: str | None = None
    to_addresses: list[str] = []


class EmailRead(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    direction: str | None = None
    subject: str | None = None
    body_text: str | None = None
    from_address: str | None = None
    to_addresses: list[str] = []
    sent_at: datetime | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class FileRead(BaseModel):
    id: UUID
    entity_type: str | None = None
    entity_id: UUID | None = None
    filename: str
    mime_type: str | None = None
    size_bytes: int | None = None
    url: str | None = None
    uploaded_by: UUID | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class TimelineEvent(BaseModel):
    id: str
    type: str
    title: str
    detail: str | None = None
    created_at: datetime
