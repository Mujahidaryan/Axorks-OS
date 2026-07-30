"""Axorks OS — Automation Schemas"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    trigger_type: str = "entity_event"
    trigger_config: Dict[str, Any] | None = None
    conditions: List[Dict[str, Any]] | None = None
    actions: List[Dict[str, Any]] | None = None
    is_active: bool = True


class WorkflowRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    name: str
    description: str | None = None
    is_active: bool
    trigger_type: str
    trigger_config: Dict[str, Any] | None = None
    conditions: List[Dict[str, Any]] | None = None
    actions: List[Dict[str, Any]] | None = None
    run_count: int
    last_run_at: datetime | None = None
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowExecutionRead(BaseModel):
    id: UUID
    workflow_id: UUID
    trigger_entity_type: str | None = None
    trigger_entity_id: UUID | None = None
    status: str
    steps_log: List[Dict[str, Any]] | None = None
    error: str | None = None
    started_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class TestTriggerRequest(BaseModel):
    entity_type: str
    entity_id: UUID | None = None
    entity_data: Dict[str, Any] = {}