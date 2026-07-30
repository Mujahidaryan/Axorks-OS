"""
Axorks OS — Contact Service
"""

from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.modules.contacts.models import Contact
from src.modules.contacts.schemas import ContactCreate, ContactUpdate


class ContactService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, org_id: UUID, ws_id: UUID, data: ContactCreate) -> Contact:
        contact = Contact(organization_id=org_id, workspace_id=ws_id, **data.model_dump())
        self.db.add(contact)
        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def get(self, contact_id: UUID, org_id: UUID) -> Contact:
        q = select(Contact).where(Contact.id == contact_id, Contact.organization_id == org_id, Contact.deleted_at.is_(None))
        res = await self.db.execute(q)
        c = res.scalar_one_or_none()
        if not c:
            raise NotFoundError("Contact")
        return c

    async def list(self, org_id: UUID, company_id: UUID | None = None, page: int = 1, per_page: int = 25) -> tuple[list[Contact], int]:
        q = select(Contact).where(Contact.organization_id == org_id, Contact.deleted_at.is_(None))
        if company_id:
            q = q.where(Contact.company_id == company_id)
        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        q = q.order_by(Contact.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        items = list((await self.db.execute(q)).scalars().all())
        return items, total

    async def update(self, contact_id: UUID, org_id: UUID, data: ContactUpdate) -> Contact:
        c = await self.get(contact_id, org_id)
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(c, k, v)
        await self.db.flush()
        await self.db.refresh(c)
        return c

    async def delete(self, contact_id: UUID, org_id: UUID) -> None:
        from datetime import UTC, datetime
        c = await self.get(contact_id, org_id)
        c.deleted_at = datetime.now(UTC)
        await self.db.flush()
