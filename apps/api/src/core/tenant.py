"""
Axorks OS — Tenant Context

Multi-tenancy context extracted from JWT on every authenticated request.
Carries org_id, workspace_id, user_id, roles, and permissions.
"""

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TenantContext:
    """
    Immutable tenant context attached to every authenticated request.

    Extracted from JWT claims by the auth dependency.
    Passed to services and repositories for tenant-scoped operations.
    """

    user_id: UUID
    org_id: UUID | None = None
    workspace_id: UUID | None = None
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)

    def has_role(self, role: str) -> bool:
        """Check if the user has a specific role."""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """Check if the user has a specific permission."""
        # Owners and admins have wildcard access
        if "owner" in self.roles or "admin" in self.roles:
            return True
        return permission in self.permissions

    def has_any_permission(self, *permissions: str) -> bool:
        """Check if the user has any of the specified permissions."""
        return any(self.has_permission(p) for p in permissions)

    @property
    def is_owner(self) -> bool:
        return "owner" in self.roles

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles or self.is_owner

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None
