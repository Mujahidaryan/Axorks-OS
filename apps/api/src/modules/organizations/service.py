"""
Axorks OS — Organization Service

Create org (auto-creates default workspace + owner role), CRUD, member management.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from src.modules.organizations.models import Organization, OrganizationMember
from src.modules.organizations.repository import OrgRepository
from src.modules.organizations.schemas import OrgCreate, OrgUpdate
from src.modules.workspaces.models import Workspace, WorkspaceMember


class OrgService:
    """Service for organization lifecycle management."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OrgRepository(db)

    async def create(self, data: OrgCreate, user_id: UUID) -> Organization:
        """
        Create an organization.
        Auto-creates a default workspace and assigns the user as owner.
        """
        # Check slug uniqueness
        existing = await self.repo.get_by_slug(data.slug)
        if existing:
            raise ConflictError(f"Organization slug '{data.slug}' is already taken")

        # Create organization
        org = Organization(name=data.name, slug=data.slug)
        org = await self.repo.create(org)

        # Add creator as owner
        member = OrganizationMember(
            organization_id=org.id,
            user_id=user_id,
            role="owner",
        )
        await self.repo.add_member(member)

        # Create default workspace
        workspace = Workspace(
            organization_id=org.id,
            name="Default",
            slug="default",
            is_default=True,
        )
        self.db.add(workspace)
        await self.db.flush()
        await self.db.refresh(workspace)

        # Add user to default workspace
        ws_member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user_id,
            role="owner",
        )
        self.db.add(ws_member)
        await self.db.flush()

        return org

    async def get(self, org_id: UUID) -> Organization:
        org = await self.repo.get_by_id(org_id)
        if not org:
            raise NotFoundError("Organization")
        return org

    async def list_for_user(self, user_id: UUID) -> list[Organization]:
        return await self.repo.list_for_user(user_id)

    async def update(self, org_id: UUID, data: OrgUpdate, user_id: UUID) -> Organization:
        org = await self.get(org_id)
        update_data = data.model_dump(exclude_unset=True)

        if "slug" in update_data:
            existing = await self.repo.get_by_slug(update_data["slug"])
            if existing and existing.id != org_id:
                raise ConflictError(f"Slug '{update_data['slug']}' is already taken")

        for key, value in update_data.items():
            setattr(org, key, value)

        await self.db.flush()
        await self.db.refresh(org)
        return org

    async def delete(self, org_id: UUID) -> None:
        from datetime import UTC, datetime
        org = await self.get(org_id)
        org.deleted_at = datetime.now(UTC)
        await self.db.flush()

    async def list_members(self, org_id: UUID) -> list[OrganizationMember]:
        return await self.repo.list_members(org_id)

    async def invite_member(
        self, org_id: UUID, user_id: UUID, role: str, invited_by: UUID
    ) -> OrganizationMember:
        existing = await self.repo.get_member(org_id, user_id)
        if existing:
            raise ConflictError("User is already a member of this organization")

        member = OrganizationMember(
            organization_id=org_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
        )
        return await self.repo.add_member(member)

    async def remove_member(self, org_id: UUID, user_id: UUID) -> None:
        member = await self.repo.get_member(org_id, user_id)
        if not member:
            raise NotFoundError("Organization member")
        if member.role == "owner":
            raise ForbiddenError("Cannot remove the organization owner")
        await self.repo.remove_member(member)
