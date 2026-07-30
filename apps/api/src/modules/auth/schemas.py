"""
Axorks OS — Auth Pydantic Schemas

Request/response DTOs for authentication flows.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    first_name: str | None = None
    last_name: str | None = None


class LoginRequest(BaseModel):
    """Email/password login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Set new password with reset token."""
    token: str
    new_password: str = Field(..., min_length=12, max_length=128)


class Enable2FAResponse(BaseModel):
    """Response with TOTP secret and QR code URI."""
    secret: str
    qr_uri: str


class Verify2FARequest(BaseModel):
    """TOTP verification request."""
    code: str = Field(..., min_length=6, max_length=6)


class ChangePasswordRequest(BaseModel):
    """Change password (requires current password)."""
    current_password: str
    new_password: str = Field(..., min_length=12, max_length=128)
