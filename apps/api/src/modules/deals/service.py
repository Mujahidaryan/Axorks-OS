"""
Axorks OS — Deal Service
"""

from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.modules.deals.models import Deal
from src.modules.deals.schemas import DealCreate, DealUpdate


class DealService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, org_id: UUID, ws_id: UUID, data: DealCreate) -> Deal:
        deal = Deal(organization_id=org_id, workspace_id=ws_id, **data.model_dump())
        self.db.add(deal)
        await self.db.flush()
        await self.db.refresh(deal)
        return deal

    async def get(self, deal_id: UUID, org_id: UUID) -> Deal:
        q = select(Deal).where(Deal.id == deal_id, Deal.organization_id == org_id, Deal.deleted_at.is_(None))
        res = await self.db.execute(q)
        d = res.scalar_one_or_none()
        if not d:
            raise NotFoundError("Deal")
        return d

    async def list(self, org_id: UUID, company_id: UUID | None = None, page: int = 1, per_page: int = 25) -> tuple[list[Deal], int]:
        q = select(Deal).where(Deal.organization_id == org_id, Deal.deleted_at.is_(None))
        if company_id:
            q = q.where(Deal.company_id == company_id)
        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        q = q.order_by(Deal.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        items = list((await self.db.execute(q)).scalars().all())
        return items, total

    async def update(self, deal_id: UUID, org_id: UUID, data: DealUpdate) -> Deal:
        d = await self.get(deal_id, org_id)
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(d, k, v)
        await self.db.flush()
        await self.db.refresh(d)
        return d

    async def delete(self, deal_id: UUID, org_id: UUID) -> None:
        from datetime import UTC, datetime
        d = await self.get(deal_id, org_id)
        d.deleted_at = datetime.now(UTC)
        await self.db.flush()
