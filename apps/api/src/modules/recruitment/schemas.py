"""Axorks OS — Recruitment Schemas"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, EmailStr


class JobOpeningCreate(BaseModel):
    title: str
    department: str | None = None
    location: str | None = None
    employment_type: str = "full_time"
    description: str | None = None
    requirements: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None


class JobOpeningRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    title: str
    department: str | None = None
    location: str | None = None
    employment_type: str
    status: str
    description: str | None = None
    requirements: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateCreate(BaseModel):
    job_opening_id: UUID | None = None
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    cv_url: str | None = None
    notes: str | None = None


class CandidateRead(BaseModel):
    id: UUID
    organization_id: UUID
    job_opening_id: UUID | None = None
    full_name: str
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    cv_url: str | None = None
    stage: str
    ai_cv_summary: str | None = None
    ai_score: int | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InterviewCreate(BaseModel):
    scheduled_at: datetime | None = None
    interview_type: str = "video"
    interviewer_ids: list[UUID] | None = None
    notes: str | None = None
    rating: int | None = None
    outcome: str | None = None


class InterviewRead(BaseModel):
    id: UUID
    candidate_id: UUID
    scheduled_at: datetime | None = None
    interview_type: str
    interviewer_ids: list[UUID] | None = None
    notes: str | None = None
    rating: int | None = None
    outcome: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
