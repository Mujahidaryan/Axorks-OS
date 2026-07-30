"""
Axorks OS — Deal API Routes
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import paginated_response, success_response
from src.core.tenant import TenantContext
from src.modules.deals.schemas import DealCreate, DealRead, DealUpdate
from src.modules.deals.service import DealService

router = APIRouter(prefix="/api/v1/deals", tags=["CRM — Deals"])


@router.post("")
async def create_deal(data: DealCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = DealService(db)
    d = await svc.create(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=DealRead.model_validate(d).model_dump(mode="json"))


@router.get("")
async def list_deals(page: int = Query(1, ge=1), per_page: int = Query(25), company_id: UUID | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = DealService(db)
    items, total = await svc.list(ctx.org_id, company_id, page, per_page)
    return paginated_response([DealRead.model_validate(i).model_dump(mode="json") for i in items], page, per_page, total)


@router.get("/{deal_id}")
async def get_deal(deal_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = DealService(db)
    d = await svc.get(deal_id, ctx.org_id)
    return success_response(data=DealRead.model_validate(d).model_dump(mode="json"))


@router.patch("/{deal_id}")
async def update_deal(deal_id: UUID, data: DealUpdate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = DealService(db)
    d = await svc.update(deal_id, ctx.org_id, data)
    return success_response(data=DealRead.model_validate(d).model_dump(mode="json"))


@router.delete("/{deal_id}")
async def delete_deal(deal_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = DealService(db)
    await svc.delete(deal_id, ctx.org_id)
    return success_response(data={"message": "Deal deleted"})
