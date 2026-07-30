"""
Axorks OS — Workspace Service
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictError, NotFoundError
from src.modules.workspaces.models import Workspace, WorkspaceMember
from src.modules.workspaces.repository import WorkspaceRepository
from src.modules.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate


class WorkspaceService:
    """Service for managing workspace lifecycle and memberships."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkspaceRepository(db)

    async def create(self, org_id: UUID, user_id: UUID, data: WorkspaceCreate) -> Workspace:
        existing = await self.repo.get_by_slug(org_id, data.slug)
        if existing:
            raise ConflictError(f"Workspace slug '{data.slug}' already exists in this organization")

        ws = Workspace(
            organization_id=org_id,
            name=data.name,
            slug=data.slug,
        )
        ws = await self.repo.create(ws)

        # Creator becomes workspace member
        member = WorkspaceMember(
            workspace_id=ws.id,
            user_id=user_id,
            role="owner",
        )
        await self.repo.add_member(member)
        return ws

    async def get(self, workspace_id: UUID, org_id: UUID) -> Workspace:
        ws = await self.repo.get_by_id(workspace_id, org_id)
        if not ws:
            raise NotFoundError("Workspace")
        return ws

    async def list_for_org(self, org_id: UUID) -> list[Workspace]:
        return await self.repo.list_for_org(org_id)

    async def update(self, workspace_id: UUID, org_id: UUID, data: WorkspaceUpdate) -> Workspace:
        ws = await self.get(workspace_id, org_id)
        update_data = data.model_dump(exclude_unset=True)

        if "slug" in update_data:
            existing = await self.repo.get_by_slug(org_id, update_data["slug"])
            if existing and existing.id != workspace_id:
                raise ConflictError(f"Slug '{update_data['slug']}' is taken")

        for key, val in update_data.items():
            setattr(ws, key, val)

        await self.db.flush()
        await self.db.refresh(ws)
        return ws

    async def list_members(self, workspace_id: UUID) -> list[WorkspaceMember]:
        return await self.repo.list_members(workspace_id)
