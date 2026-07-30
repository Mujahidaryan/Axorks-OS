"""
Axorks OS — Knowledge Base Service
"""

import re
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.modules.knowledge.models import AIPrompt, KnowledgePage
from src.modules.knowledge.schemas import AIPromptCreate, KnowledgePageCreate, KnowledgePageUpdate


class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Pages ────────────────────────────────────────────────

    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text.lower().strip())
        return re.sub(r"[\s_]+", "-", slug)

    async def create_page(self, org_id: UUID, ws_id: UUID, user_id: UUID, data: KnowledgePageCreate) -> KnowledgePage:
        base_slug = self._slugify(data.title)
        # Ensure slug uniqueness within org
        q = select(func.count()).select_from(KnowledgePage).where(
            KnowledgePage.organization_id == org_id,
            KnowledgePage.slug.like(f"{base_slug}%"),
        )
        count = (await self.db.execute(q)).scalar_one()
        slug = f"{base_slug}-{count + 1}" if count > 0 else base_slug

        page = KnowledgePage(
            organization_id=org_id,
            workspace_id=ws_id,
            parent_id=data.parent_id,
            title=data.title,
            slug=slug,
            content=data.content,
            icon=data.icon,
            page_type=data.page_type,
            is_template=data.is_template,
            created_by=user_id,
        )
        self.db.add(page)
        await self.db.flush()
        await self.db.refresh(page)
        return page

    async def get_page(self, page_id: UUID, org_id: UUID) -> KnowledgePage:
        q = select(KnowledgePage).where(KnowledgePage.id == page_id, KnowledgePage.organization_id == org_id, KnowledgePage.deleted_at.is_(None))
        res = await self.db.execute(q)
        page = res.scalar_one_or_none()
        if not page:
            raise NotFoundError("Knowledge Page")
        return page

    async def get_page_by_slug(self, slug: str, org_id: UUID) -> KnowledgePage:
        q = select(KnowledgePage).where(KnowledgePage.slug == slug, KnowledgePage.organization_id == org_id, KnowledgePage.deleted_at.is_(None))
        res = await self.db.execute(q)
        page = res.scalar_one_or_none()
        if not page:
            raise NotFoundError("Knowledge Page")
        return page

    async def list_pages(self, org_id: UUID, parent_id: UUID | None = None, page_type: str | None = None) -> list[KnowledgePage]:
        q = select(KnowledgePage).where(KnowledgePage.organization_id == org_id, KnowledgePage.deleted_at.is_(None))
        if parent_id:
            q = q.where(KnowledgePage.parent_id == parent_id)
        else:
            q = q.where(KnowledgePage.parent_id.is_(None))
        if page_type:
            q = q.where(KnowledgePage.page_type == page_type)
        q = q.order_by(KnowledgePage.sort_order.asc(), KnowledgePage.title.asc())
        return list((await self.db.execute(q)).scalars().all())

    async def update_page(self, page_id: UUID, org_id: UUID, data: KnowledgePageUpdate) -> KnowledgePage:
        page = await self.get_page(page_id, org_id)
        for k, v in data.model_dump(exclude_unset=True).items():
            if v is not None:
                setattr(page, k, v)
        if data.title:
            page.slug = self._slugify(data.title)
        await self.db.flush()
        await self.db.refresh(page)
        return page

    async def delete_page(self, page_id: UUID, org_id: UUID) -> None:
        from datetime import datetime, UTC
        page = await self.get_page(page_id, org_id)
        page.deleted_at = datetime.now(UTC)
        await self.db.flush()

    async def search_pages(self, org_id: UUID, query: str) -> list[KnowledgePage]:
        q = select(KnowledgePage).where(
            KnowledgePage.organization_id == org_id,
            KnowledgePage.deleted_at.is_(None),
            (KnowledgePage.title.ilike(f"%{query}%") | KnowledgePage.content.ilike(f"%{query}%")),
        ).limit(20)
        return list((await self.db.execute(q)).scalars().all())

    async def list_templates(self, org_id: UUID) -> list[KnowledgePage]:
        q = select(KnowledgePage).where(KnowledgePage.organization_id == org_id, KnowledgePage.is_template.is_(True), KnowledgePage.deleted_at.is_(None))
        return list((await self.db.execute(q)).scalars().all())

    # ── AI Prompt Library ────────────────────────────────────

    async def create_prompt(self, org_id: UUID, user_id: UUID, data: AIPromptCreate) -> AIPrompt:
        prompt = AIPrompt(organization_id=org_id, created_by=user_id, **data.model_dump())
        self.db.add(prompt)
        await self.db.flush()
        await self.db.refresh(prompt)
        return prompt

    async def list_prompts(self, org_id: UUID, category: str | None = None) -> list[AIPrompt]:
        q = select(AIPrompt).where(AIPrompt.organization_id == org_id)
        if category:
            q = q.where(AIPrompt.category == category)
        q = q.order_by(AIPrompt.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())
