"""
Lead Intelligence Unit Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_lead_and_list(client: AsyncClient):
    # Register & setup org
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "leadowner@axorks.com", "password": "Password123456!"},
    )
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    org_res = await client.post(
        "/api/v1/organizations",
        json={"name": "Lead Test Org", "slug": "lead-org"},
        headers=headers,
    )
    org_id = org_res.json()["data"]["id"]

    # Create Lead with minimal fields (all optional!)
    lead_res = await client.post(
        "/api/v1/leads",
        json={"business_name": "Acme Software Agency", "industry": "Technology"},
        headers=headers,
    )
    assert lead_res.status_code == 200
    lead_data = lead_res.json()["data"]
    assert lead_data["business_name"] == "Acme Software Agency"
    assert lead_data["status"] == "new"

    # List Leads
    list_res = await client.get("/api/v1/leads", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_lead_scoring(client: AsyncClient):
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "scorer@axorks.com", "password": "Password123456!"},
    )
    token = reg.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/organizations",
        json={"name": "Score Org", "slug": "score-org"},
        headers=headers,
    )

    lead_res = await client.post(
        "/api/v1/leads",
        json={
            "business_name": "Enterprise AI Inc",
            "decision_maker_title": "CTO",
            "company_size": "200-500",
            "website": "https://enterprise.ai",
        },
        headers=headers,
    )
    lead_id = lead_res.json()["data"]["id"]

    # AI Score
    score_res = await client.post(f"/api/v1/leads/{lead_id}/score", json={}, headers=headers)
    assert score_res.status_code == 200
    res_data = score_res.json()["data"]
    assert res_data["lead"]["score"] > 50
    assert "score_history" in res_data
