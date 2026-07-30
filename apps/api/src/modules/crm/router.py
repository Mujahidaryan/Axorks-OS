"""
Axorks OS — CRM Resources API Routes

Polymorphic Notes, Calls, Emails, Files, Timeline + Lead Conversion.
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.crm.schemas import (
    CallCreate, CallRead,
    EmailCreate, EmailRead,
    FileRead, NoteCreate, NoteRead,
)
from src.modules.crm.service import CRMResourceService
from src.modules.leads.service import LeadService

router = APIRouter(tags=["CRM — Resources"])


# ── Notes ──────────────────────────────────────────────────

@router.post("/api/v1/notes")
async def create_note(data: NoteCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = CRMResourceService(db)
    n = await svc.create_note(ctx.org_id, ctx.workspace_id, ctx.user_id, data)
    return success_response(data=NoteRead.model_validate(n).model_dump(mode="json"))


@router.get("/api/v1/notes")
async def list_notes(entity_type: str, entity_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = CRMResourceService(db)
    items = await svc.list_notes(entity_type, entity_id)
    return success_response(data=[NoteRead.model_validate(i).model_dump(mode="json") for i in items])


# ── Calls ──────────────────────────────────────────────────

@router.post("/api/v1/calls")
async def create_call(data: CallCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = CRMResourceService(db)
    c = await svc.create_call(ctx.org_id, ctx.workspace_id, ctx.user_id, data)
    return success_response(data=CallRead.model_validate(c).model_dump(mode="json"))


@router.get("/api/v1/calls")
async def list_calls(entity_type: str, entity_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = CRMResourceService(db)
    items = await svc.list_calls(entity_type, entity_id)
    return success_response(data=[CallRead.model_validate(i).model_dump(mode="json") for i in items])


# ── Emails ─────────────────────────────────────────────────

@router.post("/api/v1/emails")
async def create_email(data: EmailCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = CRMResourceService(db)
    e = await svc.create_email(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=EmailRead.model_validate(e).model_dump(mode="json"))


@router.get("/api/v1/emails")
async def list_emails(entity_type: str, entity_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = CRMResourceService(db)
    items = await svc.list_emails(entity_type, entity_id)
    return success_response(data=[EmailRead.model_validate(i).model_dump(mode="json") for i in items])


# ── Files ──────────────────────────────────────────────────

@router.get("/api/v1/files")
async def list_files(entity_type: str, entity_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = CRMResourceService(db)
    items = await svc.list_files(entity_type, entity_id)
    return success_response(data=[FileRead.model_validate(i).model_dump(mode="json") for i in items])


# ── Unified Timeline ──────────────────────────────────────

@router.get("/api/v1/{entity_type}/{entity_id}/timeline")
async def get_entity_timeline(entity_type: str, entity_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = CRMResourceService(db)
    events = await svc.get_timeline(entity_type, entity_id)
    return success_response(data=[e.model_dump(mode="json") for e in events])


# ── Lead → Company Conversion ─────────────────────────────

@router.post("/api/v1/leads/{lead_id}/convert")
async def convert_lead(lead_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    """Convert lead into a Company + primary Contact."""
    lead_svc = LeadService(db)
    lead = await lead_svc.get_lead(lead_id, ctx.org_id)

    lead_data = {
        "business_name": lead.business_name,
        "website": lead.website,
        "industry": lead.industry,
        "country": lead.country,
        "company_size": lead.company_size,
        "revenue_range": lead.revenue_range,
        "linkedin_url": lead.linkedin_url,
        "decision_maker_name": lead.decision_maker_name,
        "decision_maker_title": lead.decision_maker_title,
        "email": lead.email,
        "phone": lead.phone,
        "owner_id": lead.owner_id,
    }

    crm_svc = CRMResourceService(db)
    company, contact = await crm_svc.convert_lead_to_company(
        ctx.org_id, ctx.workspace_id, lead_id, ctx.user_id, lead_data
    )

    # Update lead status to won
    from src.modules.leads.models import LeadStatus
    lead.status = LeadStatus.WON
    await db.flush()

    return success_response(data={
        "company_id": str(company.id),
        "contact_id": str(contact.id),
        "message": "Lead converted to company and contact",
    })
