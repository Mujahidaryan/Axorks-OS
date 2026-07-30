"""
Axorks OS — Workspace API Routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.permissions import require_role
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceMemberRead,
    WorkspaceRead,
    WorkspaceUpdate,
)
from src.modules.workspaces.service import WorkspaceService

router = APIRouter(prefix="/api/v1/workspaces", tags=["Workspaces"])


@router.post("")
@require_role("admin")
async def create_workspace(
    data: WorkspaceCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workspace inside the organization (Admin+)."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = WorkspaceService(db)
    ws = await service.create(ctx.org_id, ctx.user_id, data)
    return success_response(data=WorkspaceRead.model_validate(ws).model_dump(mode="json"))


@router.get("")
async def list_workspaces(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List all workspaces in current organization."""
    if not ctx.org_id:
        return success_response(data=[])
    service = WorkspaceService(db)
    workspaces = await service.list_for_org(ctx.org_id)
    return success_response(
        data=[WorkspaceRead.model_validate(w).model_dump(mode="json") for w in workspaces]
    )


@router.get("/{workspace_id}")
async def get_workspace(
    workspace_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific workspace."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = WorkspaceService(db)
    ws = await service.get(workspace_id, ctx.org_id)
    return success_response(data=WorkspaceRead.model_validate(ws).model_dump(mode="json"))


@router.patch("/{workspace_id}")
@require_role("admin")
async def update_workspace(
    workspace_id: UUID,
    data: WorkspaceUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Update workspace settings (Admin+)."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = WorkspaceService(db)
    ws = await service.update(workspace_id, ctx.org_id, data)
    return success_response(data=WorkspaceRead.model_validate(ws).model_dump(mode="json"))


@router.get("/{workspace_id}/members")
async def list_workspace_members(
    workspace_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List members of a workspace."""
    service = WorkspaceService(db)
    members = await service.list_members(workspace_id)
    return success_response(
        data=[WorkspaceMemberRead.model_validate(m).model_dump(mode="json") for m in members]
    )
