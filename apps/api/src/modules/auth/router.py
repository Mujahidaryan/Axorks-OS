"""
Axorks OS — Auth API Routes

All authentication endpoints: register, login, refresh, logout,
password reset, and 2FA management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    Verify2FARequest,
)
from src.modules.auth.service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register")
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    service = AuthService(db)
    user = await service.register(data)
    tokens = await service.login(data.email, data.password)
    return success_response(data=tokens)


@router.post("/login")
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password. May return requires_2fa flag."""
    service = AuthService(db)
    result = await service.login(data.email, data.password)
    return success_response(data=result)


@router.post("/login/2fa")
async def login_2fa(
    data: Verify2FARequest,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Complete login with 2FA code."""
    service = AuthService(db)
    result = await service.verify_2fa_login(user_id, data.code)
    return success_response(data=result)


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using a valid refresh token."""
    service = AuthService(db)
    result = await service.refresh_tokens(refresh_token)
    return success_response(data=result)


@router.post("/logout")
async def logout(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Logout — revoke all refresh tokens."""
    service = AuthService(db)
    await service.logout(ctx.user_id)
    return success_response(data={"message": "Logged out successfully"})


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset link (never reveals if email exists)."""
    service = AuthService(db)
    await service.forgot_password(data.email)
    return success_response(
        data={"message": "If an account exists, a reset link has been sent"}
    )


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using a valid reset token."""
    service = AuthService(db)
    await service.reset_password(data.token, data.new_password)
    return success_response(data={"message": "Password reset successfully"})


@router.post("/2fa/enable")
async def enable_2fa(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Generate TOTP secret and QR code URI for 2FA setup."""
    service = AuthService(db)
    result = await service.enable_2fa(ctx.user_id)
    return success_response(data=result)


@router.post("/2fa/verify")
async def verify_2fa(
    data: Verify2FARequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Confirm 2FA activation with a valid TOTP code."""
    service = AuthService(db)
    await service.confirm_2fa(ctx.user_id, data.code)
    return success_response(data={"message": "2FA enabled successfully"})


@router.post("/2fa/disable")
async def disable_2fa(
    data: Verify2FARequest,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Disable 2FA (requires valid TOTP code to confirm)."""
    service = AuthService(db)
    await service.disable_2fa(ctx.user_id, data.code)
    return success_response(data={"message": "2FA disabled successfully"})
