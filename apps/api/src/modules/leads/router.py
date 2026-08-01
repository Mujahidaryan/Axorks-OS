"""
Axorks OS — Lead API Routes

REST endpoints for Lead capture, scoring, CSV import, filtering, and bulk operations.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.permissions import require_permission
from src.core.response import paginated_response, success_response
from src.core.tenant import TenantContext
from src.modules.leads.models import LeadSource, LeadStatus
from src.modules.leads.schemas import (
    BulkAssignRequest,
    BulkStatusRequest,
    CSVImportMappingRequest,
    LeadCreate,
    LeadRead,
    LeadUpdate,
    PublicLeadCaptureRequest,
    ScoreLeadRequest,
)
from src.modules.leads.service import LeadService

router = APIRouter(prefix="/api/v1/leads", tags=["Lead Intelligence"])


@router.post("/public/capture")
async def capture_public_lead(
    data: PublicLeadCaptureRequest,
    db: AsyncSession = Depends(get_db),
):
    """Zero-cost public website / form / webhook lead ingestion route (unauthenticated)."""
    service = LeadService(db)
    lead = await service.capture_public_lead(data)
    return success_response(
        data={
            "lead_id": str(lead.id),
            "status": lead.status.value if lead.status else "new",
            "message": "Lead successfully captured",
        }
    )



@router.post("")
@require_permission("leads:write")
async def create_lead(
    data: LeadCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new lead. ALL fields optional except org context!"""
    if not ctx.org_id or not ctx.workspace_id:
        raise ValueError("Organization and workspace context required")

    service = LeadService(db)
    lead = await service.create_lead(ctx.org_id, ctx.workspace_id, ctx.user_id, data)
    return success_response(data=LeadRead.model_validate(lead).model_dump(mode="json"))


@router.get("")
@require_permission("leads:read")
async def list_leads(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    status: LeadStatus | None = None,
    source: LeadSource | None = None,
    owner_id: UUID | None = None,
    tag: str | None = None,
    min_score: int | None = Query(None, ge=0, le=100),
    max_score: int | None = Query(None, ge=0, le=100),
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List leads with filtering, search, pagination, and sorting."""
    if not ctx.org_id:
        return paginated_response([], page=page, per_page=per_page, total=0)

    service = LeadService(db)
    items, total = await service.repo.list_leads(
        org_id=ctx.org_id,
        workspace_id=ctx.workspace_id,
        page=page,
        per_page=per_page,
        status=status,
        source=source,
        owner_id=owner_id,
        tag=tag,
        min_score=min_score,
        max_score=max_score,
        search_query=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return paginated_response(
        data=[LeadRead.model_validate(i).model_dump(mode="json") for i in items],
        page=page,
        per_page=per_page,
        total=total,
    )


@router.get("/stats")
@require_permission("leads:read")
async def get_lead_stats(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get lead stats for dashboard widgets."""
    if not ctx.org_id:
        return success_response(data={"total_leads": 0, "by_status": {}, "avg_score": 0})
    service = LeadService(db)
    stats = await service.repo.get_stats(ctx.org_id)
    return success_response(data=stats)


@router.get("/tags")
@require_permission("leads:read")
async def get_all_lead_tags(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get unnested autocomplete list of lead tags."""
    if not ctx.org_id:
        return success_response(data=[])
    service = LeadService(db)
    tags = await service.repo.get_all_tags(ctx.org_id)
    return success_response(data=tags)


@router.get("/{lead_id}")
@require_permission("leads:read")
async def get_lead(
    lead_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get lead details."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = LeadService(db)
    lead = await service.get_lead(lead_id, ctx.org_id)
    return success_response(data=LeadRead.model_validate(lead).model_dump(mode="json"))


@router.patch("/{lead_id}")
@require_permission("leads:write")
async def update_lead(
    lead_id: UUID,
    data: LeadUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Update lead details."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = LeadService(db)
    lead = await service.update_lead(lead_id, ctx.org_id, ctx.user_id, data)
    return success_response(data=LeadRead.model_validate(lead).model_dump(mode="json"))


@router.delete("/{lead_id}")
@require_permission("leads:delete")
async def delete_lead(
    lead_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete lead."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = LeadService(db)
    await service.delete_lead(lead_id, ctx.org_id, ctx.user_id)
    return success_response(data={"message": "Lead deleted"})


@router.post("/{lead_id}/score")
@require_permission("leads:write")
async def score_lead(
    lead_id: UUID,
    body: ScoreLeadRequest | None = None,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Score lead using AI or explicit manual score."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = LeadService(db)
    explicit_score = body.score if body else None
    reason = body.reason if body else None

    lead, history = await service.score_lead(
        lead_id, ctx.org_id, ctx.user_id, explicit_score=explicit_score, reason=reason
    )
    return success_response(
        data={
            "lead": LeadRead.model_validate(lead).model_dump(mode="json"),
            "score_history": {
                "id": str(history.id),
                "old_score": history.old_score,
                "new_score": history.new_score,
                "reason": history.reason,
                "scored_by": history.scored_by,
                "created_at": history.created_at.isoformat(),
            },
        }
    )


@router.get("/{lead_id}/score-history")
@require_permission("leads:read")
async def get_lead_score_history(
    lead_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get score change history for a lead."""
    service = LeadService(db)
    items = await service.get_score_history(lead_id)
    return success_response(
        data=[
            {
                "id": str(i.id),
                "old_score": i.old_score,
                "new_score": i.new_score,
                "reason": i.reason,
                "scored_by": i.scored_by,
                "created_at": i.created_at.isoformat(),
            }
            for i in items
        ]
    )


@router.post("/bulk-assign")
@require_permission("leads:assign")
async def bulk_assign_leads(
    body: BulkAssignRequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Bulk assign leads to a team member."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = LeadService(db)
    updated = await service.bulk_assign(ctx.org_id, body.lead_ids, body.owner_id, ctx.user_id)
    return success_response(data={"updated_count": updated})


@router.post("/bulk-status")
@require_permission("leads:write")
async def bulk_status_leads(
    body: BulkStatusRequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Bulk update lead status."""
    if not ctx.org_id:
        raise ValueError("Organization context required")
    service = LeadService(db)
    updated = await service.bulk_status(ctx.org_id, body.lead_ids, body.status, ctx.user_id)
    return success_response(data={"updated_count": updated})


@router.post("/import")
@require_permission("leads:write")
async def import_leads_csv(
    body: CSVImportMappingRequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Process CSV lead import using column mapping."""
    if not ctx.org_id or not ctx.workspace_id:
        raise ValueError("Organization and workspace context required")
    service = LeadService(db)
    job = await service.process_csv_import(ctx.org_id, ctx.workspace_id, ctx.user_id, body)
    return success_response(
        data={
            "job_id": str(job.id),
            "status": job.status,
            "imported_rows": job.imported_rows,
            "failed_rows": job.failed_rows,
            "error_log": job.error_log,
        }
    )
