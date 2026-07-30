"""
Axorks OS — Project Management Schemas
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    company_id: UUID | None = None
    deal_id: UUID | None = None
    proposal_id: UUID | None = None
    name: str
    description: str | None = None
    status: str = "planning"
    start_date: date | None = None
    end_date: date | None = None
    budget: Decimal | None = None
    currency: str = "USD"
    owner_id: UUID | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    budget: Decimal | None = None
    currency: str | None = None
    owner_id: UUID | None = None


class ProjectRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    company_id: UUID | None = None
    deal_id: UUID | None = None
    proposal_id: UUID | None = None
    name: str
    description: str | None = None
    status: str
    start_date: date | None = None
    end_date: date | None = None
    budget: Decimal | None = None
    currency: str
    owner_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SprintCreate(BaseModel):
    project_id: UUID
    name: str
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "planned"


class SprintRead(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    project_id: UUID | None = None
    sprint_id: UUID | None = None
    parent_id: UUID | None = None
    epic_id: UUID | None = None
    title: str
    description: str | None = None
    type: str = "task"  # epic, story, task, subtask, bug
    status: str = "backlog"  # backlog, todo, in_progress, review, done
    priority: str = "medium"
    assignee_id: UUID | None = None
    due_date: date | None = None
    estimate_hours: Decimal | None = None


class TaskUpdate(BaseModel):
    project_id: UUID | None = None
    sprint_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    type: str | None = None
    status: str | None = None
    priority: str | None = None
    assignee_id: UUID | None = None
    due_date: date | None = None
    estimate_hours: Decimal | None = None
    sort_order: int | None = None


class TaskRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    project_id: UUID | None = None
    sprint_id: UUID | None = None
    parent_id: UUID | None = None
    epic_id: UUID | None = None
    title: str
    description: str | None = None
    type: str
    status: str
    priority: str
    assignee_id: UUID | None = None
    due_date: date | None = None
    estimate_hours: Decimal | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TimeEntryCreate(BaseModel):
    task_id: UUID | None = None
    project_id: UUID | None = None
    hours: Decimal
    description: str | None = None
    logged_date: date


class TimeEntryRead(BaseModel):
    id: UUID
    organization_id: UUID
    task_id: UUID | None = None
    project_id: UUID | None = None
    user_id: UUID
    hours: Decimal
    description: str | None = None
    logged_date: date
    created_at: datetime

    model_config = {"from_attributes": True}
