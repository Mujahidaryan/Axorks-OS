"""
Axorks OS — User API Routes

GET  /api/v1/users/me              — Get current user profile
PATCH /api/v1/users/me             — Update profile
PATCH /api/v1/users/me/preferences — Update preferences
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.users.schemas import UserPreferencesUpdate, UserRead, UserUpdate
from src.modules.users.service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me")
async def get_current_user(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get the current authenticated user's profile."""
    service = UserService(db)
    user = await service.get_by_id(ctx.user_id)
    return success_response(data=UserRead.model_validate(user).model_dump(mode="json"))


@router.patch("/me")
async def update_current_user(
    data: UserUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    service = UserService(db)
    user = await service.update_profile(ctx.user_id, data)
    return success_response(data=UserRead.model_validate(user).model_dump(mode="json"))


@router.patch("/me/preferences")
async def update_preferences(
    data: UserPreferencesUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Update user preferences (theme, sidebar, notifications)."""
    service = UserService(db)
    prefs = data.model_dump(exclude_unset=True)
    user = await service.update_preferences(ctx.user_id, prefs)
    return success_response(data={"preferences": user.preferences})
