"""Encrypted storage for environment variable values."""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from src.core.config import get_settings

settings = get_settings()


def _fernet() -> Fernet:
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.auth_secret.encode()).digest())
    return Fernet(key)


def encrypt_value(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt_value(value_encrypted: str) -> str:
    try:
        return _fernet().decrypt(value_encrypted.encode()).decode()
    except InvalidToken:
        # Legacy base64-encoded values from earlier Phase 7 scaffold
        return base64.b64decode(value_encrypted.encode()).decode()
