"""
Axorks OS — Enterprise IAM, RBAC & Screen/Call Recording API Routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_user, get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.iam.schemas import (
    DepartmentCreate,
    IAMUserCreate,
    IAMUserRead,
    IAMUserUpdate,
    RecordingCreate,
    RecordingRead,
    RoleCreate,
)
from src.modules.iam.service import IAMService
from src.modules.users.models import User

router = APIRouter(prefix="/api/v1/iam", tags=["Identity & Access Management"])


@router.get("/dashboard")
async def get_founder_dashboard(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Founder Dashboard overview metrics and recent activity."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    dashboard_data = await service.get_founder_dashboard(org_id)
    return success_response(data=dashboard_data)


@router.get("/users")
async def list_iam_users(
    search: str | None = None,
    department: str | None = None,
    role: str | None = None,
    status: str | None = None,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List employees with filtering and search."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    users = await service.list_users(
        org_id=org_id, search=search, department=department, role=role, status=status
    )
    return success_response(
        data=[IAMUserRead.model_validate(u).model_dump(mode="json") for u in users]
    )


@router.post("/users")
async def create_iam_user(
    body: IAMUserCreate,
    current_user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new employee and assign role & department."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    user = await service.create_user(org_id, current_user, body)
    return success_response(data=IAMUserRead.model_validate(user).model_dump(mode="json"))


@router.get("/users/{user_id}")
async def get_iam_user(
    user_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get employee profile details."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    user = await service.get_user_by_id(user_id, org_id)
    return success_response(data=IAMUserRead.model_validate(user).model_dump(mode="json"))


@router.patch("/users/{user_id}")
async def update_iam_user(
    user_id: UUID,
    body: IAMUserUpdate,
    current_user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Update employee details, role, or status."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    user = await service.update_user(user_id, org_id, current_user, body)
    return success_response(data=IAMUserRead.model_validate(user).model_dump(mode="json"))


@router.post("/users/{user_id}/{action}")
async def perform_user_action(
    user_id: UUID,
    action: str,
    current_user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Perform security action (suspend, reactivate, lock, unlock, reset-password, impersonate)."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)

    if action == "impersonate":
        user = await service.get_user_by_id(user_id, org_id)
        # Generate impersonation token response
        return success_response(
            data={
                "impersonated_user_id": str(user.id),
                "impersonated_email": user.email,
                "token": f"impersonate_token_{user.id}",
                "message": f"Impersonating employee {user.first_name} {user.last_name}",
            }
        )

    user = await service.perform_user_action(user_id, org_id, current_user, action)
    return success_response(
        data={
            "user": IAMUserRead.model_validate(user).model_dump(mode="json"),
            "action": action,
            "message": f"Action '{action}' executed successfully",
        }
    )


@router.get("/roles")
async def list_iam_roles(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List predefined and custom RBAC roles with permissions matrix."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    roles = await service.list_roles(org_id)
    return success_response(
        data=[
            {
                "id": str(r.id),
                "name": r.name,
                "description": r.description,
                "is_custom": r.is_custom,
                "grant_percentage": r.grant_percentage,
                "permissions": r.permissions,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in roles
        ]
    )


@router.post("/roles")
async def create_iam_role(
    body: RoleCreate,
    current_user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new custom enterprise RBAC role."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    role = await service.create_role(org_id, current_user, body)
    return success_response(
        data={
            "id": str(role.id),
            "name": role.name,
            "description": role.description,
            "is_custom": role.is_custom,
            "grant_percentage": role.grant_percentage,
            "permissions": role.permissions,
        }
    )


@router.get("/departments")
async def list_iam_departments(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List departments and employee counts."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    depts = await service.list_departments(org_id)
    return success_response(data=depts)


@router.post("/departments")
async def create_iam_department(
    body: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new organizational department."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    dept = await service.create_department(org_id, current_user, body)
    return success_response(
        data={
            "id": str(dept.id),
            "name": dept.name,
            "code": dept.code,
            "description": dept.description,
        }
    )


@router.get("/recordings")
async def list_recordings(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List Founder screen and call recordings."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    recs = await service.list_recordings(org_id)
    return success_response(
        data=[RecordingRead.model_validate(r).model_dump(mode="json") for r in recs]
    )


@router.post("/recordings")
async def create_recording(
    body: RecordingCreate,
    current_user: User = Depends(get_current_user),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Save a screen or call recording record."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    rec = await service.create_recording(org_id, current_user, body)
    return success_response(data=RecordingRead.model_validate(rec).model_dump(mode="json"))


@router.get("/audit-logs")
async def list_audit_logs(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get security audit logs feed."""
    org_id = ctx.org_id or UUID("00000000-0000-0000-0000-000000000001")
    service = IAMService(db)
    logs = await service.list_audit_logs(org_id)
    return success_response(
        data=[
            {
                "id": str(l.id),
                "actor_email": l.actor_email,
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "old_values": l.old_values,
                "new_values": l.new_values,
                "ip_address": l.ip_address,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ]
    )
