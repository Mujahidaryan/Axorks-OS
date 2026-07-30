"""
Axorks OS — Knowledge Base Schemas
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class KnowledgePageCreate(BaseModel):
    title: str
    content: str | None = None
    parent_id: UUID | None = None
    icon: str | None = "📄"
    page_type: str = "page"
    is_template: bool = False


class KnowledgePageUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    icon: str | None = None
    page_type: str | None = None


class KnowledgePageRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    parent_id: UUID | None = None
    title: str
    slug: str
    content: str | None = None
    icon: str | None = None
    page_type: str
    is_template: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIPromptCreate(BaseModel):
    title: str
    category: str | None = "general"
    prompt_text: str
    description: str | None = None
    is_public: bool = False


class AIPromptRead(BaseModel):
    id: UUID
    organization_id: UUID
    title: str
    category: str | None = None
    prompt_text: str
    description: str | None = None
    is_public: bool
    created_at: datetime

    model_config = {"from_attributes": True}
