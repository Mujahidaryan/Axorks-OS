"""
Axorks OS — Company Service
"""

from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.modules.companies.models import Company
from src.modules.companies.schemas import CompanyCreate, CompanyUpdate


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, org_id: UUID, ws_id: UUID, data: CompanyCreate) -> Company:
        company = Company(
            organization_id=org_id, workspace_id=ws_id, **data.model_dump()
        )
        self.db.add(company)
        await self.db.flush()
        await self.db.refresh(company)
        return company

    async def get(self, company_id: UUID, org_id: UUID) -> Company:
        q = select(Company).where(Company.id == company_id, Company.organization_id == org_id, Company.deleted_at.is_(None))
        res = await self.db.execute(q)
        company = res.scalar_one_or_none()
        if not company:
            raise NotFoundError("Company")
        return company

    async def list(self, org_id: UUID, page: int = 1, per_page: int = 25, search: str | None = None) -> tuple[list[Company], int]:
        q = select(Company).where(Company.organization_id == org_id, Company.deleted_at.is_(None))
        if search:
            q = q.where(Company.name.ilike(f"%{search}%"))
        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar_one()
        q = q.order_by(Company.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        items = list((await self.db.execute(q)).scalars().all())
        return items, total

    async def update(self, company_id: UUID, org_id: UUID, data: CompanyUpdate) -> Company:
        company = await self.get(company_id, org_id)
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(company, k, v)
        await self.db.flush()
        await self.db.refresh(company)
        return company

    async def delete(self, company_id: UUID, org_id: UUID) -> None:
        from datetime import UTC, datetime
        company = await self.get(company_id, org_id)
        company.deleted_at = datetime.now(UTC)
        await self.db.flush()
