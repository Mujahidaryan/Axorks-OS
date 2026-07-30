"""
Axorks OS — Permission System

Role-to-permission mapping and permission enforcement decorator.
Roles: owner > admin > manager > member > viewer > client
Permissions follow resource:action pattern.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import HTTPException, status

from src.core.tenant import TenantContext

# ── Default Role → Permission Mapping ────────────────────────

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "owner": ["*"],  # Wildcard — full access
    "admin": ["*"],  # Same as owner for now; custom roles will differentiate
    "manager": [
        "leads:read", "leads:write", "leads:delete", "leads:assign",
        "crm:read", "crm:write",
        "projects:read", "projects:write", "projects:manage",
        "proposals:read", "proposals:write",
        "dev:read", "dev:write",
        "finance:read",
        "knowledge:read", "knowledge:write",
        "marketing:read", "marketing:write",
        "recruitment:read", "recruitment:write",
        "hr:read",
        "analytics:read",
        "settings:read",
        "users:read", "users:invite",
        "notifications:read", "notifications:write",
        "ai:use",
    ],
    "member": [
        "leads:read", "leads:write",
        "crm:read", "crm:write",
        "projects:read", "projects:write",
        "proposals:read", "proposals:write",
        "dev:read", "dev:write",
        "knowledge:read", "knowledge:write",
        "analytics:read",
        "notifications:read", "notifications:write",
        "ai:use",
    ],
    "viewer": [
        "leads:read",
        "crm:read",
        "projects:read",
        "proposals:read",
        "dev:read",
        "finance:read",
        "knowledge:read",
        "analytics:read",
        "notifications:read",
    ],
    "client": [
        "portal:read",
        "portal:write",
    ],
}

# ── Role Hierarchy ───────────────────────────────────────────

ROLE_HIERARCHY = {
    "owner": 100,
    "admin": 90,
    "manager": 70,
    "member": 50,
    "viewer": 20,
    "client": 10,
}


def get_permissions_for_role(role: str) -> list[str]:
    """Get all permissions granted to a role."""
    return ROLE_PERMISSIONS.get(role, [])


def get_highest_role(roles: list[str]) -> str:
    """Get the highest-ranking role from a list of roles."""
    if not roles:
        return "viewer"
    return max(roles, key=lambda r: ROLE_HIERARCHY.get(r, 0))


def role_at_least(user_role: str, required_role: str) -> bool:
    """Check if user's role is at least as high as the required role."""
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    return user_level >= required_level


# ── Permission Check Functions ───────────────────────────────


def check_permission(ctx: TenantContext, permission: str) -> None:
    """
    Check if the tenant context has the required permission.
    Raises HTTPException 403 if not.
    """
    if not ctx.has_permission(permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {permission} required",
        )


def require_permission(permission: str) -> Callable:
    """
    Decorator for FastAPI route handlers requiring a specific permission.

    Usage:
        @router.get("/leads")
        @require_permission("leads:read")
        async def list_leads(ctx: TenantContext = Depends(get_tenant_context)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Find TenantContext in kwargs
            ctx = kwargs.get("ctx") or kwargs.get("tenant")
            if ctx is None:
                # Search through args for TenantContext
                for arg in args:
                    if isinstance(arg, TenantContext):
                        ctx = arg
                        break

            if ctx is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            check_permission(ctx, permission)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: str) -> Callable:
    """
    Decorator for FastAPI route handlers requiring a minimum role level.

    Usage:
        @router.delete("/organizations/{id}")
        @require_role("admin")
        async def delete_org(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = kwargs.get("ctx") or kwargs.get("tenant")
            if ctx is None:
                for arg in args:
                    if isinstance(arg, TenantContext):
                        ctx = arg
                        break

            if ctx is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            highest = get_highest_role(ctx.roles)
            if not role_at_least(highest, role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role}' or higher required",
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
