"""
Axorks OS — Workspace Repository
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.workspaces.models import Workspace, WorkspaceMember


class WorkspaceRepository:
    """Database repository for Workspace entities."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, workspace_id: UUID, org_id: UUID | None = None) -> Workspace | None:
        query = select(Workspace).where(
            Workspace.id == workspace_id, Workspace.deleted_at.is_(None)
        )
        if org_id:
            query = query.where(Workspace.organization_id == org_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, org_id: UUID, slug: str) -> Workspace | None:
        query = select(Workspace).where(
            Workspace.organization_id == org_id,
            Workspace.slug == slug,
            Workspace.deleted_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_for_org(self, org_id: UUID) -> list[Workspace]:
        query = select(Workspace).where(
            Workspace.organization_id == org_id, Workspace.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, workspace: Workspace) -> Workspace:
        self.db.add(workspace)
        await self.db.flush()
        await self.db.refresh(workspace)
        return workspace

    async def add_member(self, member: WorkspaceMember) -> WorkspaceMember:
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def list_members(self, workspace_id: UUID) -> list[WorkspaceMember]:
        query = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
