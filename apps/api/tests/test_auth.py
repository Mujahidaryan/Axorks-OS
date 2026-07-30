"""
Authentication Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Register
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@axorks.com",
            "password": "Password123456!",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert reg_res.status_code == 200
    data = reg_res.json()["data"]
    assert "access_token" in data
    assert data["user"]["email"] == "test@axorks.com"

    # Login
    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@axorks.com",
            "password": "Password123456!",
        },
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()["data"]
