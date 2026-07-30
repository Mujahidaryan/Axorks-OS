"""
Axorks OS — Settings API Routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.permissions import require_role
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.settings.schemas import OrgSettingsUpdate, WorkspaceSettingsUpdate
from src.modules.settings.service import SettingsService

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


@router.patch("/organization")
@require_role("admin")
async def update_org_settings(
    data: OrgSettingsUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Update organization settings (Admin+)."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = SettingsService(db)
    updated = await service.update_org_settings(
        ctx.org_id, data.model_dump(exclude_unset=True), ctx.user_id
    )
    return success_response(data={"settings": updated})


@router.patch("/workspaces/{workspace_id}")
@require_role("admin")
async def update_workspace_settings(
    workspace_id: UUID,
    data: WorkspaceSettingsUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Update workspace settings (Admin+)."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = SettingsService(db)
    updated = await service.update_workspace_settings(
        workspace_id, ctx.org_id, data.model_dump(exclude_unset=True)
    )
    return success_response(data={"settings": updated})
