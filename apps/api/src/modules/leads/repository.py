"""
Axorks OS — Lead Repository
"""

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.leads.models import Lead, LeadSource, LeadStatus
from src.shared.base_repository import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    """Database repository for Lead operations."""

    model = Lead

    async def list_leads(
        self,
        org_id: UUID,
        workspace_id: UUID | None = None,
        page: int = 1,
        per_page: int = 25,
        status: LeadStatus | None = None,
        source: LeadSource | None = None,
        owner_id: UUID | None = None,
        tag: str | None = None,
        min_score: int | None = None,
        max_score: int | None = None,
        search_query: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Lead], int]:
        """List leads with multi-tenancy, filters, search, and pagination."""
        query = select(Lead).where(
            Lead.organization_id == org_id, Lead.deleted_at.is_(None)
        )

        if workspace_id:
            query = query.where(Lead.workspace_id == workspace_id)
        if status:
            query = query.where(Lead.status == status)
        if source:
            query = query.where(Lead.source == source)
        if owner_id:
            query = query.where(Lead.owner_id == owner_id)
        if min_score is not None:
            query = query.where(Lead.score >= min_score)
        if max_score is not None:
            query = query.where(Lead.score <= max_score)
        if tag:
            query = query.where(Lead.tags.any(tag))

        if search_query and search_query.strip():
            st = f"%{search_query.strip()}%"
            query = query.where(
                (Lead.business_name.ilike(st))
                | (Lead.decision_maker_name.ilike(st))
                | (Lead.email.ilike(st))
                | (Lead.notes.ilike(st))
            )

        # Count total
        count_q = select(func.count()).select_from(query.subquery())
        total_res = await self.db.execute(count_q)
        total = total_res.scalar_one()

        # Sorting
        if hasattr(Lead, sort_by):
            col = getattr(Lead, sort_by)
            query = query.order_by(col.desc() if sort_order == "desc" else col.asc())

        # Pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_stats(self, org_id: UUID) -> dict[str, Any]:
        """Get summary stats for lead dashboard widgets."""
        total_q = select(func.count()).where(
            Lead.organization_id == org_id, Lead.deleted_at.is_(None)
        )
        total = (await self.db.execute(total_q)).scalar_one()

        # Group by status
        status_q = (
            select(Lead.status, func.count())
            .where(Lead.organization_id == org_id, Lead.deleted_at.is_(None))
            .group_by(Lead.status)
        )
        status_res = (await self.db.execute(status_q)).fetchall()
        by_status = {str(r[0].value if hasattr(r[0], 'value') else r[0]): r[1] for r in status_res}

        # Average score
        avg_q = select(func.avg(Lead.score)).where(
            Lead.organization_id == org_id, Lead.deleted_at.is_(None)
        )
        avg_score = (await self.db.execute(avg_q)).scalar_one() or 0

        return {
            "total_leads": total,
            "by_status": by_status,
            "avg_score": round(float(avg_score), 1),
        }

    async def get_all_tags(self, org_id: UUID) -> list[str]:
        """Get list of all distinct tags in organization."""
        sql = select(func.unnest(Lead.tags)).where(
            Lead.organization_id == org_id, Lead.deleted_at.is_(None)
        ).distinct()
        res = await self.db.execute(sql)
        return [r[0] for r in res.fetchall() if r[0]]
