"""
Axorks OS — RBAC Service
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.rbac.defaults import DEFAULT_ROLES
from src.modules.rbac.models import Role, RoleAssignment


class RBACService:
    """Service for custom roles and permission checks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_default_roles(self, org_id: UUID) -> list[Role]:
        """Seed default system roles for a new organization."""
        roles = []
        for role_key, spec in DEFAULT_ROLES.items():
            role = Role(
                organization_id=org_id,
                name=spec["name"],
                description=spec["description"],
                is_system=True,
                permissions=spec["permissions"],
            )
            self.db.add(role)
            roles.append(role)
        await self.db.flush()
        return roles

    async def get_org_roles(self, org_id: UUID) -> list[Role]:
        query = select(Role).where(Role.organization_id == org_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def assign_role(
        self, role_id: UUID, user_id: UUID, scope_type: str, scope_id: UUID
    ) -> RoleAssignment:
        assignment = RoleAssignment(
            role_id=role_id,
            user_id=user_id,
            scope_type=scope_type,
            scope_id=scope_id,
        )
        self.db.add(assignment)
        await self.db.flush()
        return assignment
