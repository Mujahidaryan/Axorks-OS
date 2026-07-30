"""
Axorks OS — Security Utilities

JWT encode/decode (HS256), password hashing (bcrypt), TOTP 2FA.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pyotp
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import get_settings

settings = get_settings()

# ── Password Hashing ────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ──────────────────────────────────────────────

ALGORITHM = "HS256"


def create_access_token(
    user_id: UUID,
    org_id: UUID | None = None,
    workspace_id: UUID | None = None,
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
) -> str:
    """Create a short-lived JWT access token (15 min default)."""
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    claims = {
        "sub": str(user_id),
        "iat": now,
        "exp": expire,
        "type": "access",
    }

    if org_id:
        claims["org_id"] = str(org_id)
    if workspace_id:
        claims["workspace_id"] = str(workspace_id)
    if roles:
        claims["roles"] = roles
    if permissions:
        claims["permissions"] = permissions

    return jwt.encode(claims, settings.auth_secret, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """Create a long-lived refresh token (7 day default)."""
    now = datetime.now(UTC)
    expire = now + timedelta(days=settings.refresh_token_expire_days)

    claims = {
        "sub": str(user_id),
        "iat": now,
        "exp": expire,
        "type": "refresh",
    }

    return jwt.encode(claims, settings.auth_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Raises JWTError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.auth_secret, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise


def verify_access_token(token: str) -> dict:
    """Decode an access token and verify it's the correct type."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    return payload


def verify_refresh_token(token: str) -> dict:
    """Decode a refresh token and verify it's the correct type."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise JWTError("Invalid token type")
    return payload


# ── TOTP Two-Factor Authentication ──────────────────────────


def generate_totp_secret() -> str:
    """Generate a new TOTP secret for 2FA setup."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Generate a provisioning URI for QR code display."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="Axorks OS")


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against the stored secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
