"""Axorks OS — Integrations Router"""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.integrations.schemas import IntegrationConnect, IntegrationRead, WebhookCreate, WebhookRead
from src.modules.integrations.service import IntegrationService

router = APIRouter(prefix="/api/v1/integrations", tags=["Integrations"])


@router.get("/catalog")
async def get_catalog(db: AsyncSession = Depends(get_db)):
    svc = IntegrationService(db)
    return success_response(data=svc.get_catalog())


@router.post("/connect")
async def connect_integration(data: IntegrationConnect, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = IntegrationService(db)
    item = await svc.connect(ctx.org_id, data)
    return success_response(data=IntegrationRead.model_validate(item).model_dump(mode="json"))


@router.post("/disconnect/{provider}")
async def disconnect_integration(provider: str, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = IntegrationService(db)
    await svc.disconnect(ctx.org_id, provider)
    return success_response(data={"disconnected": True})


@router.get("/connected")
async def list_connected(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = IntegrationService(db)
    items = await svc.list_connected(ctx.org_id)
    return success_response(data=[IntegrationRead.model_validate(i).model_dump(mode="json") for i in items])


@router.post("/webhooks")
async def create_webhook(data: WebhookCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = IntegrationService(db)
    wh = await svc.create_webhook(ctx.org_id, data)
    return success_response(data=WebhookRead.model_validate(wh).model_dump(mode="json"))


@router.get("/webhooks")
async def list_webhooks(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = IntegrationService(db)
    webhooks = await svc.list_webhooks(ctx.org_id)
    return success_response(data=[WebhookRead.model_validate(w).model_dump(mode="json") for w in webhooks])


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = IntegrationService(db)
    await svc.delete_webhook(webhook_id, ctx.org_id)
    return success_response(data={"deleted": True})