"""
Axorks OS — Phase 10: Knowledge Base Tests

Tests page CRUD, nested pages, slug generation, search, templates, and AI prompt library.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_knowledge_base_flow(auth_client: AsyncClient):
    # 1. Create Knowledge Page
    res = await auth_client.post(
        "/api/v1/knowledge/pages",
        json={"title": "Coding Standards", "content": "## Git Flow\n\nAlways use feature branches.", "page_type": "sop", "icon": "📋"},
    )
    assert res.status_code == 200
    page = res.json()["data"]
    page_id = page["id"]
    assert page["title"] == "Coding Standards"
    assert page["slug"] == "coding-standards"
    assert page["page_type"] == "sop"

    # 2. Create Child Page (nested)
    res = await auth_client.post(
        "/api/v1/knowledge/pages",
        json={"title": "Python Style Guide", "parent_id": page_id, "content": "Use ruff for linting.", "page_type": "page"},
    )
    assert res.status_code == 200
    child = res.json()["data"]
    assert child["parent_id"] == page_id

    # 3. List Root Pages
    res = await auth_client.get("/api/v1/knowledge/pages")
    assert res.status_code == 200
    assert any(p["id"] == page_id for p in res.json()["data"])

    # 4. List Child Pages
    res = await auth_client.get(f"/api/v1/knowledge/pages?parent_id={page_id}")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 5. Get Page by ID
    res = await auth_client.get(f"/api/v1/knowledge/pages/{page_id}")
    assert res.status_code == 200
    assert res.json()["data"]["title"] == "Coding Standards"

    # 6. Get Page by Slug
    res = await auth_client.get("/api/v1/knowledge/pages/by-slug/coding-standards")
    assert res.status_code == 200

    # 7. Update Page Content
    res = await auth_client.patch(
        f"/api/v1/knowledge/pages/{page_id}",
        json={"content": "## Git Flow\n\nAlways use feature branches.\n\n## PR Reviews\n\nMinimum 2 approvals required."},
    )
    assert res.status_code == 200

    # 8. Search Pages
    res = await auth_client.get("/api/v1/knowledge/pages/search?q=Git+Flow")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 9. Create AI Prompt
    res = await auth_client.post(
        "/api/v1/knowledge/prompts",
        json={
            "title": "Sales Discovery Call Summary",
            "category": "sales",
            "prompt_text": "Summarize this sales call transcript and extract: 1) Pain points 2) Budget signals 3) Decision timeline 4) Next steps.",
            "description": "Use after any discovery call recording.",
        },
    )
    assert res.status_code == 200
    assert res.json()["data"]["category"] == "sales"

    # 10. List Prompts
    res = await auth_client.get("/api/v1/knowledge/prompts")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 11. List Prompts by Category
    res = await auth_client.get("/api/v1/knowledge/prompts?category=sales")
    assert res.status_code == 200
    assert all(p["category"] == "sales" for p in res.json()["data"])

    # 12. Delete Page (soft delete)
    res = await auth_client.delete(f"/api/v1/knowledge/pages/{page_id}")
    assert res.status_code == 200
