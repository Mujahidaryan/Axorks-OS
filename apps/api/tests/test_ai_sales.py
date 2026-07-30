"""
Axorks OS — Phase 4: AI Sales Assistant Tests

Tests question suggestions, summarization, requirement detection, budget/complexity estimation,
follow-up email generation, objection detection, action item extraction, and pending action confirmation workflow.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_sales_endpoints(auth_client: AsyncClient):
    # 1. Create a company & deal for context
    c_res = await auth_client.post("/api/v1/companies", json={"name": "Cyberdyne Systems", "industry": "AI & Robotics"})
    company_id = c_res.json()["data"]["id"]

    d_res = await auth_client.post("/api/v1/deals", json={"title": "Skynet Core", "company_id": company_id, "value": 500000.00})
    deal_id = d_res.json()["data"]["id"]

    # 2. Suggest Questions
    res = await auth_client.post(
        "/api/v1/ai/sales/suggest-questions",
        json={"entity_type": "deal", "entity_id": deal_id},
    )
    assert res.status_code == 200
    assert "questions" in res.json()["data"]
    assert len(res.json()["data"]["questions"]) >= 3

    # 3. Summarize Text
    res = await auth_client.post(
        "/api/v1/ai/sales/summarize",
        json={"entity_type": "deal", "entity_id": deal_id, "text_content": "Discussed core API design, security, and timeline."},
    )
    assert res.status_code == 200
    assert "summary" in res.json()["data"]

    # 4. Detect Requirements
    res = await auth_client.post(
        "/api/v1/ai/sales/detect-requirements",
        json={"conversation_text": "We need user auth, RBAC, analytics dashboard, and PostgreSQL database."},
    )
    assert res.status_code == 200
    assert "functional_requirements" in res.json()["data"]

    # 5. Estimate Budget
    res = await auth_client.post(
        "/api/v1/ai/sales/estimate-budget",
        json={"requirements": ["Auth", "RBAC", "Dashboard"], "industry": "Software"},
    )
    assert res.status_code == 200
    assert "recommended_budget" in res.json()["data"]

    # 6. Estimate Complexity
    res = await auth_client.post(
        "/api/v1/ai/sales/estimate-complexity",
        json={"requirements": ["Auth", "RBAC", "Dashboard"]},
    )
    assert res.status_code == 200
    assert "t_shirt_size" in res.json()["data"]

    # 7. Suggest Tech
    res = await auth_client.post(
        "/api/v1/ai/sales/suggest-tech",
        json={"requirements": ["Auth", "Dashboard"]},
    )
    assert res.status_code == 200
    assert "recommended_stack" in res.json()["data"]

    # 8. Suggest Followup Email
    res = await auth_client.post(
        "/api/v1/ai/sales/suggest-followup",
        json={"call_outcome": "positive", "key_points": ["Budget approved", "Start next week"]},
    )
    assert res.status_code == 200
    assert "subject" in res.json()["data"]

    # 9. Detect Objections
    res = await auth_client.post(
        "/api/v1/ai/sales/detect-objections",
        json={"transcript_text": "The price is a bit high for our initial budget."},
    )
    assert res.status_code == 200
    assert "objections_detected" in res.json()["data"]

    # 10. Extract Action Items
    res = await auth_client.post(
        "/api/v1/ai/sales/action-items",
        json={"conversation_text": "John will send NDA tomorrow. Sarah to schedule demo."},
    )
    assert res.status_code == 200
    assert "action_items" in res.json()["data"]


@pytest.mark.asyncio
async def test_ai_action_confirmation_workflow(auth_client: AsyncClient):
    # Create deal
    d_res = await auth_client.post("/api/v1/deals", json={"title": "Robotics Integration", "status": "open", "stage": "Discovery"})
    deal_id = d_res.json()["data"]["id"]

    # Request CRM update suggestion (creates pending action confirmation)
    res = await auth_client.post(
        "/api/v1/ai/sales/update-crm",
        json={"entity_type": "deal", "entity_id": deal_id, "text_source": "Prospect agreed to review formal proposal next Tuesday."},
    )
    assert res.status_code == 200
    action = res.json()["data"]
    action_id = action["id"]
    assert action["status"] == "pending"

    # List pending actions
    res = await auth_client.get(f"/api/v1/ai/actions?entity_type=deal&entity_id={deal_id}")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # Confirm action (executes CRM deal update)
    res = await auth_client.post(f"/api/v1/ai/actions/{action_id}/confirm")
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "confirmed"

    # Verify deal stage updated to Proposal
    res = await auth_client.get(f"/api/v1/deals/{deal_id}")
    assert res.status_code == 200
    assert res.json()["data"]["stage"] == "Proposal"
