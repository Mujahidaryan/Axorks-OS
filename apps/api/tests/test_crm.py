"""
Axorks OS — Phase 3: One-Page CRM Tests

Tests Companies, Contacts, Deals, Notes, Calls, Emails, Files, Unified Timeline, and Lead Conversion.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_company_crud(auth_client: AsyncClient):
    # Create company
    res = await auth_client.post(
        "/api/v1/companies",
        json={
            "name": "Acme Corp",
            "website": "https://acme.com",
            "industry": "Software",
            "country": "USA",
            "size": "50-100",
        },
    )
    assert res.status_code == 200
    company = res.json()["data"]
    company_id = company["id"]
    assert company["name"] == "Acme Corp"

    # List companies
    res = await auth_client.get("/api/v1/companies")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # Get company
    res = await auth_client.get(f"/api/v1/companies/{company_id}")
    assert res.status_code == 200
    assert res.json()["data"]["id"] == company_id

    # Update company
    res = await auth_client.patch(f"/api/v1/companies/{company_id}", json={"industry": "AI & SaaS"})
    assert res.status_code == 200
    assert res.json()["data"]["industry"] == "AI & SaaS"

    # Delete company
    res = await auth_client.delete(f"/api/v1/companies/{company_id}")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_contact_crud(auth_client: AsyncClient):
    # Create contact
    res = await auth_client.post(
        "/api/v1/contacts",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@acme.com",
            "title": "CTO",
            "is_primary": True,
        },
    )
    assert res.status_code == 200
    contact = res.json()["data"]
    contact_id = contact["id"]
    assert contact["first_name"] == "Jane"

    # List contacts
    res = await auth_client.get("/api/v1/contacts")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # Delete contact
    res = await auth_client.delete(f"/api/v1/contacts/{contact_id}")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_deal_crud(auth_client: AsyncClient):
    # Create deal
    res = await auth_client.post(
        "/api/v1/deals",
        json={
            "title": "Enterprise Cloud Migration",
            "value": 150000.00,
            "currency": "USD",
            "stage": "Proposal",
            "probability": 75,
        },
    )
    assert res.status_code == 200
    deal = res.json()["data"]
    deal_id = deal["id"]
    assert deal["title"] == "Enterprise Cloud Migration"

    # Update deal status to won
    res = await auth_client.patch(f"/api/v1/deals/{deal_id}", json={"status": "won"})
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "won"


@pytest.mark.asyncio
async def test_polymorphic_crm_resources_and_timeline(auth_client: AsyncClient):
    # Create a test company to attach resources to
    res = await auth_client.post("/api/v1/companies", json={"name": "Stark Industries"})
    company_id = res.json()["data"]["id"]

    # Add Note
    res = await auth_client.post(
        "/api/v1/notes",
        json={"entity_type": "company", "entity_id": company_id, "content": "Met with Tony Stark. Loves the demo."},
    )
    assert res.status_code == 200

    # Log Call
    res = await auth_client.post(
        "/api/v1/calls",
        json={
            "entity_type": "company",
            "entity_id": company_id,
            "direction": "outbound",
            "duration_seconds": 600,
            "outcome": "Follow-up scheduled",
            "called_at": "2026-07-29T10:00:00Z",
        },
    )
    assert res.status_code == 200

    # Unified Timeline
    res = await auth_client.get(f"/api/v1/company/{company_id}/timeline")
    assert res.status_code == 200
    timeline = res.json()["data"]
    assert len(timeline) >= 2


@pytest.mark.asyncio
async def test_lead_conversion(auth_client: AsyncClient):
    # Create a lead
    res = await auth_client.post(
        "/api/v1/leads",
        json={
            "business_name": "Wayne Enterprises",
            "decision_maker_name": "Bruce Wayne",
            "email": "bruce@wayne.com",
            "industry": "Defense",
        },
    )
    lead_id = res.json()["data"]["id"]

    # Convert lead to company + contact
    res = await auth_client.post(f"/api/v1/leads/{lead_id}/convert")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "company_id" in data
    assert "contact_id" in data
