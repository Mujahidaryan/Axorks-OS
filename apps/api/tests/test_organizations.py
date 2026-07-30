"""
Organization Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_organization(client: AsyncClient):
    # Register user
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "orgowner@axorks.com",
            "password": "Password123456!",
            "first_name": "Org",
            "last_name": "Owner",
        },
    )
    token = reg_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Org
    org_res = await client.post(
        "/api/v1/organizations",
        json={"name": "Axorks Dev House", "slug": "axorks-dev"},
        headers=headers,
    )
    assert org_res.status_code == 200
    org_data = org_res.json()["data"]
    assert org_data["name"] == "Axorks Dev House"
    assert org_data["slug"] == "axorks-dev"

    # List Orgs
    list_res = await client.get("/api/v1/organizations", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1
