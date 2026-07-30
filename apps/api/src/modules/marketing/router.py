"""Axorks OS — Marketing Router"""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.marketing.schemas import CampaignCreate, CampaignRead, ContentItemCreate, ContentItemRead, EmailCampaignCreate, EmailCampaignRead
from src.modules.marketing.service import MarketingService

router = APIRouter(prefix="/api/v1/marketing", tags=["Marketing"])


@router.post("/campaigns")
async def create_campaign(data: CampaignCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = MarketingService(db); c = await svc.create_campaign(ctx.org_id, ctx.workspace_id, ctx.user_id, data)
    return success_response(data=CampaignRead.model_validate(c).model_dump(mode="json"))


@router.get("/campaigns")
async def list_campaigns(status: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = MarketingService(db); items = await svc.list_campaigns(ctx.org_id, status)
    return success_response(data=[CampaignRead.model_validate(i).model_dump(mode="json") for i in items])


@router.patch("/campaigns/{campaign_id}")
async def update_campaign(campaign_id: UUID, updates: dict, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = MarketingService(db); c = await svc.update_campaign(campaign_id, ctx.org_id, updates)
    return success_response(data=CampaignRead.model_validate(c).model_dump(mode="json"))


@router.post("/content")
async def create_content(data: ContentItemCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = MarketingService(db); item = await svc.create_content_item(ctx.org_id, data)
    return success_response(data=ContentItemRead.model_validate(item).model_dump(mode="json"))


@router.get("/content")
async def list_content(campaign_id: UUID | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = MarketingService(db); items = await svc.list_content_items(ctx.org_id, campaign_id)
    return success_response(data=[ContentItemRead.model_validate(i).model_dump(mode="json") for i in items])


@router.post("/email-campaigns")
async def create_email_campaign(data: EmailCampaignCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = MarketingService(db); ec = await svc.create_email_campaign(ctx.org_id, data)
    return success_response(data=EmailCampaignRead.model_validate(ec).model_dump(mode="json"))


@router.get("/funnel-stats")
async def get_funnel_stats(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = MarketingService(db); stats = await svc.get_funnel_stats(ctx.org_id)
    return success_response(data=stats)
