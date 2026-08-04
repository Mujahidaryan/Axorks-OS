"""
Axorks OS — Enterprise IAM & RBAC Pydantic Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class IAMUserCreate(BaseModel):
    email: EmailStr | str
    password: str | None = None
    first_name: str
    last_name: str
    display_name: str | None = None
    employee_id: str | None = None
    phone: str | None = None
    cnic: str | None = None
    department: str | None = "Development"
    designation: str | None = "Software Engineer"
    joining_date: str | None = None
    employment_type: str = "full_time"  # full_time, part_time, contract, intern
    reporting_manager_id: UUID | None = None
    role: str = "member"  # founder, co_founder, ceo, cto, project_manager, etc.
    status: str = "active"  # active, inactive, suspended, on_leave, resigned, terminated, locked, pending_invitation
    avatar_url: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    notes: str | None = None


class IAMUserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    phone: str | None = None
    cnic: str | None = None
    department: str | None = None
    designation: str | None = None
    joining_date: str | None = None
    employment_type: str | None = None
    reporting_manager_id: UUID | None = None
    role: str | None = None
    status: str | None = None
    avatar_url: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    notes: str | None = None


class IAMUserRead(BaseModel):
    id: UUID
    organization_id: UUID
    email: str
    first_name: str
    last_name: str
    display_name: str | None = None
    employee_id: str | None = None
    phone: str | None = None
    cnic: str | None = None
    department: str | None = None
    designation: str | None = None
    joining_date: str | None = None
    employment_type: str | None = None
    reporting_manager_id: UUID | None = None
    role: str
    status: str
    avatar_url: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    notes: str | None = None
    failed_attempts: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    last_login_browser: str | None = None
    last_login_device: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    is_custom: bool = True
    grant_percentage: int = 100
    permissions: list[str] = []


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    grant_percentage: int | None = None
    permissions: list[str] | None = None


class RoleRead(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None = None
    is_custom: bool
    grant_percentage: int
    permissions: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class DepartmentCreate(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    head_id: UUID | None = None


class DepartmentRead(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    code: str | None = None
    description: str | None = None
    head_id: UUID | None = None
    employee_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogRead(BaseModel):
    id: UUID
    organization_id: UUID
    actor_id: UUID | None = None
    actor_email: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    old_values: dict | None = None
    new_values: dict | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordingCreate(BaseModel):
    user_id: UUID | None = None
    recording_type: str = "screen"  # screen, call, interaction
    title: str
    file_url: str | None = None
    duration_seconds: int = 0
    metadata_json: dict = {}


class RecordingRead(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID | None = None
    recorded_by_id: UUID
    recording_type: str
    title: str
    file_url: str | None = None
    duration_seconds: int
    metadata_json: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginSessionRead(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    user_email: str | None = None
    user_name: str | None = None
    session_token: str
    ip_address: str | None = None
    country: str | None = None
    browser: str | None = None
    os: str | None = None
    device: str | None = None
    status: str
    login_at: datetime
    last_activity_at: datetime

    model_config = {"from_attributes": True}


class FounderDashboardResponse(BaseModel):
    total_employees: int
    online_employees: int
    offline_employees: int
    locked_accounts: int
    suspended_accounts: int
    pending_invitations: int
    todays_logins: int
    failed_attempts: int
    recent_audit_logs: list[dict] = []
    latest_joined: list[dict] = []
    recent_recordings: list[dict] = []
