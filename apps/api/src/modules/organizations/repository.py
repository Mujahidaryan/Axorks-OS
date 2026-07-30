"""
Axorks OS — Organization Repository

Database queries with tenant isolation for organizations.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organizations.models import Organization, OrganizationMember


class OrgRepository:
    """Repository for organization database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, org_id: UUID) -> Organization | None:
        query = select(Organization).where(
            Organization.id == org_id, Organization.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Organization | None:
        query = select(Organization).where(
            Organization.slug == slug, Organization.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> list[Organization]:
        query = (
            select(Organization)
            .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
            .where(OrganizationMember.user_id == user_id, Organization.deleted_at.is_(None))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, org: Organization) -> Organization:
        self.db.add(org)
        await self.db.flush()
        await self.db.refresh(org)
        return org

    async def get_member(self, org_id: UUID, user_id: UUID) -> OrganizationMember | None:
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_members(self, org_id: UUID) -> list[OrganizationMember]:
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_member(self, member: OrganizationMember) -> OrganizationMember:
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def remove_member(self, member: OrganizationMember) -> None:
        await self.db.delete(member)
        await self.db.flush()
