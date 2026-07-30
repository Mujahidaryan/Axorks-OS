"""Axorks OS — Marketing Service"""
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import NotFoundError
from src.modules.marketing.models import Campaign, ContentItem, EmailCampaign
from src.modules.marketing.schemas import CampaignCreate, ContentItemCreate, EmailCampaignCreate


class MarketingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_campaign(self, org_id: UUID, ws_id: UUID, user_id: UUID, data: CampaignCreate) -> Campaign:
        c = Campaign(organization_id=org_id, workspace_id=ws_id, created_by=user_id, **data.model_dump())
        self.db.add(c); await self.db.flush(); await self.db.refresh(c); return c

    async def list_campaigns(self, org_id: UUID, status: str | None = None) -> list[Campaign]:
        q = select(Campaign).where(Campaign.organization_id == org_id, Campaign.deleted_at.is_(None))
        if status: q = q.where(Campaign.status == status)
        return list((await self.db.execute(q.order_by(Campaign.created_at.desc()))).scalars().all())

    async def get_campaign(self, campaign_id: UUID, org_id: UUID) -> Campaign:
        res = await self.db.execute(select(Campaign).where(Campaign.id == campaign_id, Campaign.organization_id == org_id, Campaign.deleted_at.is_(None)))
        c = res.scalar_one_or_none()
        if not c: raise NotFoundError("Campaign")
        return c

    async def update_campaign(self, campaign_id: UUID, org_id: UUID, updates: dict) -> Campaign:
        c = await self.get_campaign(campaign_id, org_id)
        for k, v in updates.items():
            if v is not None: setattr(c, k, v)
        await self.db.flush(); await self.db.refresh(c); return c

    async def create_content_item(self, org_id: UUID, data: ContentItemCreate) -> ContentItem:
        item = ContentItem(organization_id=org_id, **data.model_dump())
        self.db.add(item); await self.db.flush(); await self.db.refresh(item); return item

    async def list_content_items(self, org_id: UUID, campaign_id: UUID | None = None) -> list[ContentItem]:
        q = select(ContentItem).where(ContentItem.organization_id == org_id)
        if campaign_id: q = q.where(ContentItem.campaign_id == campaign_id)
        return list((await self.db.execute(q.order_by(ContentItem.scheduled_at.asc()))).scalars().all())

    async def create_email_campaign(self, org_id: UUID, data: EmailCampaignCreate) -> EmailCampaign:
        ec = EmailCampaign(organization_id=org_id, **data.model_dump())
        self.db.add(ec); await self.db.flush(); await self.db.refresh(ec); return ec

    async def get_funnel_stats(self, org_id: UUID) -> dict:
        """Returns lead funnel stages from leads table."""
        from src.modules.leads.models import Lead
        stages = ["new", "contacted", "qualified", "proposal", "negotiation", "won", "lost"]
        result = {}
        for stage in stages:
            q = select(func.count()).select_from(Lead).where(Lead.organization_id == org_id, Lead.status == stage, Lead.deleted_at.is_(None))
            count = (await self.db.execute(q)).scalar_one()
            result[stage] = count
        return result
