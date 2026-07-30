"""
Axorks OS — Knowledge Base API Router
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.knowledge.schemas import (
    AIPromptCreate, AIPromptRead,
    KnowledgePageCreate, KnowledgePageRead, KnowledgePageUpdate,
)
from src.modules.knowledge.service import KnowledgeService

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Base"])


# ── Pages ────────────────────────────────────────────────

@router.post("/pages")
async def create_page(data: KnowledgePageCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    page = await svc.create_page(ctx.org_id, ctx.workspace_id, ctx.user_id, data)
    return success_response(data=KnowledgePageRead.model_validate(page).model_dump(mode="json"))


@router.get("/pages")
async def list_pages(parent_id: UUID | None = None, page_type: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    pages = await svc.list_pages(ctx.org_id, parent_id, page_type)
    return success_response(data=[KnowledgePageRead.model_validate(p).model_dump(mode="json") for p in pages])


@router.get("/pages/search")
async def search_pages(q: str = Query(...), ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    pages = await svc.search_pages(ctx.org_id, q)
    return success_response(data=[KnowledgePageRead.model_validate(p).model_dump(mode="json") for p in pages])


@router.get("/templates")
async def list_templates(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    pages = await svc.list_templates(ctx.org_id)
    return success_response(data=[KnowledgePageRead.model_validate(p).model_dump(mode="json") for p in pages])


@router.get("/pages/{page_id}")
async def get_page(page_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    page = await svc.get_page(page_id, ctx.org_id)
    return success_response(data=KnowledgePageRead.model_validate(page).model_dump(mode="json"))


@router.get("/pages/by-slug/{slug}")
async def get_page_by_slug(slug: str, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    page = await svc.get_page_by_slug(slug, ctx.org_id)
    return success_response(data=KnowledgePageRead.model_validate(page).model_dump(mode="json"))


@router.patch("/pages/{page_id}")
async def update_page(page_id: UUID, data: KnowledgePageUpdate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    page = await svc.update_page(page_id, ctx.org_id, data)
    return success_response(data=KnowledgePageRead.model_validate(page).model_dump(mode="json"))


@router.delete("/pages/{page_id}")
async def delete_page(page_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    await svc.delete_page(page_id, ctx.org_id)
    return success_response(data={"deleted": True})


# ── AI Prompt Library ────────────────────────────────────

@router.post("/prompts")
async def create_prompt(data: AIPromptCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    prompt = await svc.create_prompt(ctx.org_id, ctx.user_id, data)
    return success_response(data=AIPromptRead.model_validate(prompt).model_dump(mode="json"))


@router.get("/prompts")
async def list_prompts(category: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = KnowledgeService(db)
    prompts = await svc.list_prompts(ctx.org_id, category)
    return success_response(data=[AIPromptRead.model_validate(p).model_dump(mode="json") for p in prompts])
