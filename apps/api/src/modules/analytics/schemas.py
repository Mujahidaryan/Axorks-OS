"""Axorks OS — Analytics Schemas"""
from uuid import UUID
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel

class MetricCreate(BaseModel):
    name: str
    data: Dict[str, Any]

class MetricRead(BaseModel):
    id: UUID; organization_id: UUID; workspace_id: UUID; name: str; data: Dict[str, Any]
    created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}

class DashboardCreate(BaseModel):
    title: str
    layout: Dict[str, Any]

class DashboardRead(BaseModel):
    id: UUID; organization_id: UUID; workspace_id: UUID; title: str; layout: Dict[str, Any]
    created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}
