"""Axorks OS — HR Schemas"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    user_id: UUID | None = None
    full_name: str
    email: EmailStr | None = None
    department: str | None = None
    job_title: str | None = None
    employment_type: str = "full_time"
    hire_date: date | None = None
    salary: Decimal | None = None
    currency: str = "USD"
    avatar_url: str | None = None


class EmployeeRead(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID | None = None
    full_name: str
    email: str | None = None
    department: str | None = None
    job_title: str | None = None
    employment_type: str
    hire_date: date | None = None
    salary: Decimal | None = None
    currency: str
    status: str
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeaveRequestCreate(BaseModel):
    employee_id: UUID
    leave_type: str = "annual"
    start_date: date
    end_date: date
    days_count: int | None = None
    reason: str | None = None


class LeaveRequestRead(BaseModel):
    id: UUID
    organization_id: UUID
    employee_id: UUID
    leave_type: str
    start_date: date
    end_date: date
    days_count: int | None = None
    reason: str | None = None
    status: str
    approved_by: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PerformanceReviewCreate(BaseModel):
    employee_id: UUID
    reviewer_id: UUID | None = None
    review_period: str | None = "Q1-2026"
    overall_rating: int | None = 5
    strengths: str | None = None
    improvements: str | None = None
    goals_next_period: str | None = None


class PerformanceReviewRead(BaseModel):
    id: UUID
    organization_id: UUID
    employee_id: UUID
    reviewer_id: UUID | None = None
    review_period: str | None = None
    overall_rating: int | None = None
    strengths: str | None = None
    improvements: str | None = None
    goals_next_period: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}