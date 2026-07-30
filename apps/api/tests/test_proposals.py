"""
Axorks OS — Phase 5: Proposal Generator Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_proposal_crud_and_ai_generation(auth_client: AsyncClient):
    res = await auth_client.post(
        "/api/v1/proposals",
        json={
            "title": "Cloud Platform Modernization",
            "type": "proposal",
            "total_value": 50000.00,
            "currency": "USD",
            "content": {
                "sections": [{"title": "Scope", "content": "Modernize cloud services", "order": 1}],
                "pricing": {"items": [{"description": "Cloud Architecture", "amount": 50000.00}]},
            },
        },
    )
    assert res.status_code == 200
    proposal = res.json()["data"]
    proposal_id = proposal["id"]
    assert proposal["title"] == "Cloud Platform Modernization"
    assert proposal["version"] == 1

    res = await auth_client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"title": "Cloud Platform Modernization (v2)"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["title"] == "Cloud Platform Modernization (v2)"
    assert res.json()["data"]["version"] == 2

    res = await auth_client.get("/api/v1/proposals")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    res = await auth_client.post(
        "/api/v1/proposals/generate",
        json={
            "proposal_type": "technical_proposal",
            "additional_notes": "AI Powered SaaS Platform",
        },
    )
    assert res.status_code == 200
    ai_prop = res.json()["data"]
    assert "content" in ai_prop
    assert "sections" in ai_prop["content"]

    res = await auth_client.get(f"/api/v1/proposals/{proposal_id}/versions")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 2

    res = await auth_client.post(f"/api/v1/proposals/{proposal_id}/export/pdf")
    assert res.status_code == 200
    assert res.json()["data"]["download_path"]

    res = await auth_client.get(f"/api/v1/proposals/{proposal_id}/download/pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 100

    res = await auth_client.post(f"/api/v1/proposals/{proposal_id}/export/docx")
    assert res.status_code == 200
    assert res.json()["data"]["download_path"]

    res = await auth_client.get(f"/api/v1/proposals/{proposal_id}/download/docx")
    assert res.status_code == 200
    assert "wordprocessingml" in res.headers["content-type"]

    res = await auth_client.post(
        f"/api/v1/proposals/{proposal_id}/send",
        json={"recipient_email": "client@example.com", "subject": "Your Proposal"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "sent"


@pytest.mark.asyncio
async def test_proposal_templates(auth_client: AsyncClient):
    res = await auth_client.post(
        "/api/v1/proposal-templates",
        json={
            "name": "Standard Consultancy SOW Template",
            "type": "sow",
            "default_content": {"sections": [{"title": "Default Scope", "content": "Template content"}]},
        },
    )
    assert res.status_code == 200
    template_id = res.json()["data"]["id"]

    res = await auth_client.get("/api/v1/proposal-templates")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    res = await auth_client.patch(
        f"/api/v1/proposal-templates/{template_id}",
        json={"name": "Updated SOW Template"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "Updated SOW Template"

    res = await auth_client.post(
        "/api/v1/proposals/generate",
        json={"proposal_type": "sow", "template_id": template_id},
    )
    assert res.status_code == 200
    assert res.json()["data"]["type"] == "sow"

    res = await auth_client.delete(f"/api/v1/proposal-templates/{template_id}")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_proposal_improve_section(auth_client: AsyncClient):
    res = await auth_client.post(
        "/api/v1/proposals",
        json={
            "title": "Improve Section Test",
            "type": "proposal",
            "content": {
                "sections": [{"title": "Overview", "content": "Basic overview text.", "order": 1}],
            },
        },
    )
    proposal_id = res.json()["data"]["id"]

    res = await auth_client.post(
        f"/api/v1/proposals/{proposal_id}/ai/improve-section",
        json={"section_index": 0, "instruction": "Make it more professional"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["content"]
