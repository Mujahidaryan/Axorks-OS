"""
Axorks OS — Contact API Routes
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import paginated_response, success_response
from src.core.tenant import TenantContext
from src.modules.contacts.schemas import ContactCreate, ContactRead, ContactUpdate
from src.modules.contacts.service import ContactService

router = APIRouter(prefix="/api/v1/contacts", tags=["CRM — Contacts"])


@router.post("")
async def create_contact(data: ContactCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ContactService(db)
    c = await svc.create(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=ContactRead.model_validate(c).model_dump(mode="json"))


@router.get("")
async def list_contacts(page: int = Query(1, ge=1), per_page: int = Query(25, ge=1, le=100), company_id: UUID | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ContactService(db)
    items, total = await svc.list(ctx.org_id, company_id, page, per_page)
    return paginated_response([ContactRead.model_validate(i).model_dump(mode="json") for i in items], page, per_page, total)


@router.get("/{contact_id}")
async def get_contact(contact_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ContactService(db)
    c = await svc.get(contact_id, ctx.org_id)
    return success_response(data=ContactRead.model_validate(c).model_dump(mode="json"))


@router.patch("/{contact_id}")
async def update_contact(contact_id: UUID, data: ContactUpdate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ContactService(db)
    c = await svc.update(contact_id, ctx.org_id, data)
    return success_response(data=ContactRead.model_validate(c).model_dump(mode="json"))


@router.delete("/{contact_id}")
async def delete_contact(contact_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ContactService(db)
    await svc.delete(contact_id, ctx.org_id)
    return success_response(data={"message": "Contact deleted"})
