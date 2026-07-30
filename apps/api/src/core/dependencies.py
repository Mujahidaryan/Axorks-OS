"""
Axorks OS — FastAPI Dependencies

Reusable dependency injection for database sessions, authentication,
and tenant context across all routes.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.permissions import get_permissions_for_role
from src.core.security import verify_access_token
from src.core.tenant import TenantContext

# Bearer token scheme — extracts JWT from Authorization header
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UUID:
    """
    Extract and validate user ID from the JWT access token.
    Raises 401 if token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        return UUID(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UUID | None:
    """
    Optionally extract user ID from JWT.
    Returns None if no token provided (for public endpoints).
    """
    if credentials is None:
        return None
    try:
        payload = verify_access_token(credentials.credentials)
        user_id = payload.get("sub")
        return UUID(user_id) if user_id else None
    except JWTError:
        return None


async def get_tenant_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> TenantContext:
    """
    Build a TenantContext from JWT claims.
    This is the primary dependency for authenticated, tenant-scoped routes.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
        )

    org_id = payload.get("org_id")
    workspace_id = payload.get("workspace_id")
    roles = payload.get("roles", [])

    # Build permission list from roles
    permissions = payload.get("permissions", [])
    if not permissions:
        for role in roles:
            permissions.extend(get_permissions_for_role(role))
        permissions = list(set(permissions))

    return TenantContext(
        user_id=UUID(user_id),
        org_id=UUID(org_id) if org_id else None,
        workspace_id=UUID(workspace_id) if workspace_id else None,
        roles=roles,
        permissions=permissions,
    )


# Re-export get_db for convenience
__all__ = [
    "get_db",
    "get_current_user_id",
    "get_optional_user_id",
    "get_tenant_context",
]
