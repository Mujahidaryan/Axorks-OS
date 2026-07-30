"""
Axorks OS — Organization API Routes

CRUD operations and member management for Organizations.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.permissions import require_permission, require_role
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.organizations.schemas import (
    InviteMemberRequest,
    OrgCreate,
    OrgMemberRead,
    OrgRead,
    OrgUpdate,
)
from src.modules.organizations.service import OrgService

router = APIRouter(prefix="/api/v1/organizations", tags=["Organizations"])


@router.post("")
async def create_organization(
    data: OrgCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new organization. Current user becomes owner."""
    service = OrgService(db)
    org = await service.create(data, ctx.user_id)
    return success_response(data=OrgRead.model_validate(org).model_dump(mode="json"))


@router.get("")
async def list_user_organizations(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List all organizations the current user belongs to."""
    service = OrgService(db)
    orgs = await service.list_for_user(ctx.user_id)
    return success_response(
        data=[OrgRead.model_validate(o).model_dump(mode="json") for o in orgs]
    )


@router.get("/{org_id}")
async def get_organization(
    org_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get organization details."""
    service = OrgService(db)
    org = await service.get(org_id)
    return success_response(data=OrgRead.model_validate(org).model_dump(mode="json"))


@router.patch("/{org_id}")
@require_role("admin")
async def update_organization(
    org_id: UUID,
    data: OrgUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Update organization settings (admin/owner only)."""
    service = OrgService(db)
    org = await service.update(org_id, data, ctx.user_id)
    return success_response(data=OrgRead.model_validate(org).model_dump(mode="json"))


@router.delete("/{org_id}")
@require_role("owner")
async def delete_organization(
    org_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete an organization (owner only)."""
    service = OrgService(db)
    await service.delete(org_id)
    return success_response(data={"message": "Organization deleted"})


@router.get("/{org_id}/members")
async def list_org_members(
    org_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List organization members."""
    service = OrgService(db)
    members = await service.list_members(org_id)
    return success_response(
        data=[OrgMemberRead.model_validate(m).model_dump(mode="json") for m in members]
    )


@router.delete("/{org_id}/members/{user_id}")
@require_role("admin")
async def remove_org_member(
    org_id: UUID,
    user_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from the organization (admin/owner only)."""
    service = OrgService(db)
    await service.remove_member(org_id, user_id)
    return success_response(data={"message": "Member removed"})
