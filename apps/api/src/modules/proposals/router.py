"""
Axorks OS — Proposal Generator API Router
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.permissions import require_permission
from src.core.response import paginated_response, success_response
from src.core.tenant import TenantContext
from src.modules.proposals.schemas import (
    ProposalCreate,
    ProposalGenerateRequest,
    ProposalImproveSectionRequest,
    ProposalRead,
    ProposalSendRequest,
    ProposalTemplateCreate,
    ProposalTemplateRead,
    ProposalTemplateUpdate,
    ProposalUpdate,
    ProposalVersionRead,
)
from src.modules.proposals.service import ProposalService

router = APIRouter(tags=["Proposal Generator"])


def _serialize_proposal(proposal) -> dict:
    svc_data = ProposalRead.model_validate(proposal).model_dump(mode="json")
    svc_data["milestones"] = [
        {
            "id": str(m.id),
            "title": m.title,
            "description": m.description,
            "amount": float(m.amount) if m.amount else None,
            "due_date": m.due_date.isoformat() if m.due_date else None,
            "sort_order": m.sort_order,
        }
        for m in sorted(proposal.milestones, key=lambda x: x.sort_order)
    ]
    return svc_data


@router.post("/api/v1/proposals")
@require_permission("proposals:write")
async def create_proposal(
    data: ProposalCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    prop = await svc.create(ctx.org_id, ctx.workspace_id, ctx.user_id, data)
    return success_response(data=_serialize_proposal(prop))


@router.post("/api/v1/proposals/generate")
@require_permission("proposals:write")
async def generate_proposal(
    req: ProposalGenerateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    prop = await svc.generate_proposal(ctx.org_id, ctx.workspace_id, ctx.user_id, req)
    return success_response(data=_serialize_proposal(prop))


@router.get("/api/v1/proposals")
@require_permission("proposals:read")
async def list_proposals(
    page: int = Query(1, ge=1),
    per_page: int = Query(25),
    status: str | None = None,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    items, total = await svc.list(ctx.org_id, page, per_page, status)
    return paginated_response([_serialize_proposal(i) for i in items], page, per_page, total)


@router.get("/api/v1/proposals/{proposal_id}")
@require_permission("proposals:read")
async def get_proposal(
    proposal_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    prop = await svc.get(proposal_id, ctx.org_id)
    return success_response(data=_serialize_proposal(prop))


@router.patch("/api/v1/proposals/{proposal_id}")
@require_permission("proposals:write")
async def update_proposal(
    proposal_id: UUID,
    data: ProposalUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    prop = await svc.update(proposal_id, ctx.org_id, ctx.user_id, data)
    return success_response(data=_serialize_proposal(prop))


@router.post("/api/v1/proposals/{proposal_id}/ai/improve-section")
@require_permission("proposals:write")
async def improve_proposal_section(
    proposal_id: UUID,
    data: ProposalImproveSectionRequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    result = await svc.improve_section(
        proposal_id, ctx.org_id, ctx.workspace_id, ctx.user_id, data
    )
    return success_response(data=result)


@router.get("/api/v1/proposals/{proposal_id}/versions")
@require_permission("proposals:read")
async def list_proposal_versions(
    proposal_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    versions = await svc.list_versions(proposal_id, ctx.org_id)
    return success_response(
        data=[ProposalVersionRead.model_validate(v).model_dump(mode="json") for v in versions]
    )


@router.post("/api/v1/proposals/{proposal_id}/send")
@require_permission("proposals:write")
async def send_proposal(
    proposal_id: UUID,
    data: ProposalSendRequest = ProposalSendRequest(),
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    prop = await svc.send_proposal(proposal_id, ctx.org_id, data)
    return success_response(data=_serialize_proposal(prop))


@router.post("/api/v1/proposals/{proposal_id}/export/pdf")
@require_permission("proposals:read")
async def export_pdf(
    proposal_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    pdf_bytes = await svc.export_pdf_bytes(proposal_id, ctx.org_id)
    return success_response(data={
        "filename": f"proposal-{proposal_id}.pdf",
        "content_type": "application/pdf",
        "size_bytes": len(pdf_bytes),
        "download_path": f"/api/v1/proposals/{proposal_id}/download/pdf",
    })


@router.get("/api/v1/proposals/{proposal_id}/download/pdf")
@require_permission("proposals:read")
async def download_pdf(
    proposal_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    pdf_bytes = await svc.export_pdf_bytes(proposal_id, ctx.org_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="proposal-{proposal_id}.pdf"'},
    )


@router.post("/api/v1/proposals/{proposal_id}/export/docx")
@require_permission("proposals:read")
async def export_docx(
    proposal_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    docx_bytes = await svc.export_docx_bytes(proposal_id, ctx.org_id)
    return success_response(data={
        "filename": f"proposal-{proposal_id}.docx",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "size_bytes": len(docx_bytes),
        "download_path": f"/api/v1/proposals/{proposal_id}/download/docx",
    })


@router.get("/api/v1/proposals/{proposal_id}/download/docx")
@require_permission("proposals:read")
async def download_docx(
    proposal_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    docx_bytes = await svc.export_docx_bytes(proposal_id, ctx.org_id)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="proposal-{proposal_id}.docx"'},
    )


@router.delete("/api/v1/proposals/{proposal_id}")
@require_permission("proposals:write")
async def delete_proposal(
    proposal_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    await svc.delete(proposal_id, ctx.org_id)
    return success_response(data={"message": "Proposal deleted"})


# ── Proposal Templates ──────────────────────────────────────


@router.post("/api/v1/proposal-templates")
@require_permission("proposals:write")
async def create_template(
    data: ProposalTemplateCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    tmpl = await svc.create_template(ctx.org_id, data)
    return success_response(data=ProposalTemplateRead.model_validate(tmpl).model_dump(mode="json"))


@router.get("/api/v1/proposal-templates")
@require_permission("proposals:read")
async def list_templates(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    items = await svc.list_templates(ctx.org_id)
    return success_response(
        data=[ProposalTemplateRead.model_validate(i).model_dump(mode="json") for i in items]
    )


@router.patch("/api/v1/proposal-templates/{template_id}")
@require_permission("proposals:write")
async def update_template(
    template_id: UUID,
    data: ProposalTemplateUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    tmpl = await svc.update_template(template_id, ctx.org_id, data)
    return success_response(data=ProposalTemplateRead.model_validate(tmpl).model_dump(mode="json"))


@router.delete("/api/v1/proposal-templates/{template_id}")
@require_permission("proposals:write")
async def delete_template(
    template_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = ProposalService(db)
    await svc.delete_template(template_id, ctx.org_id)
    return success_response(data={"message": "Template deleted"})
