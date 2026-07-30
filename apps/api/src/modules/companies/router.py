"""
Axorks OS — Company API Routes
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import paginated_response, success_response
from src.core.tenant import TenantContext
from src.modules.companies.schemas import CompanyCreate, CompanyRead, CompanyUpdate
from src.modules.companies.service import CompanyService

router = APIRouter(prefix="/api/v1/companies", tags=["CRM — Companies"])


@router.post("")
async def create_company(data: CompanyCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = CompanyService(db)
    c = await svc.create(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=CompanyRead.model_validate(c).model_dump(mode="json"))


@router.get("")
async def list_companies(page: int = Query(1, ge=1), per_page: int = Query(25, ge=1, le=100), search: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = CompanyService(db)
    items, total = await svc.list(ctx.org_id, page, per_page, search)
    return paginated_response([CompanyRead.model_validate(i).model_dump(mode="json") for i in items], page, per_page, total)


@router.get("/{company_id}")
async def get_company(company_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = CompanyService(db)
    c = await svc.get(company_id, ctx.org_id)
    return success_response(data=CompanyRead.model_validate(c).model_dump(mode="json"))


@router.patch("/{company_id}")
async def update_company(company_id: UUID, data: CompanyUpdate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = CompanyService(db)
    c = await svc.update(company_id, ctx.org_id, data)
    return success_response(data=CompanyRead.model_validate(c).model_dump(mode="json"))


@router.delete("/{company_id}")
async def delete_company(company_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = CompanyService(db)
    await svc.delete(company_id, ctx.org_id)
    return success_response(data={"message": "Company deleted"})
