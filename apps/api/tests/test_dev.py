"""
Axorks OS — Phase 7: Development Hub Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dev_hub_flow(auth_client: AsyncClient):
    # 1. Connect VCS
    res = await auth_client.post(
        "/api/v1/dev/integrations/vcs",
        json={"provider": "github", "access_token": "mock_github_token", "account_username": "axorks-devs"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["provider"] == "github"

    # 2. List integrations
    res = await auth_client.get("/api/v1/dev/integrations/vcs")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 3. Connect repository
    res = await auth_client.post(
        "/api/v1/dev/repos",
        json={
            "provider": "github",
            "external_repo_id": "repo_999",
            "name": "axorks-api-core",
            "full_name": "axorks/axorks-api-core",
            "html_url": "https://github.com/axorks/axorks-api-core",
            "default_branch": "main",
        },
    )
    assert res.status_code == 200
    repo = res.json()["data"]
    repo_id = repo["id"]
    assert repo["name"] == "axorks-api-core"

    # 4. List repositories
    res = await auth_client.get("/api/v1/dev/repos")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 5. Sync repository
    res = await auth_client.post(f"/api/v1/dev/repos/{repo_id}/sync")
    assert res.status_code == 200

    # 6. List PRs
    res = await auth_client.get(f"/api/v1/dev/repos/{repo_id}/prs")
    assert res.status_code == 200
    prs = res.json()["data"]
    assert len(prs) >= 1
    pr_id = prs[0]["id"]

    # 7. List issues
    res = await auth_client.get(f"/api/v1/dev/repos/{repo_id}/issues")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 8. AI code review
    res = await auth_client.post(f"/api/v1/dev/prs/{pr_id}/ai-review")
    assert res.status_code == 200
    assert res.json()["data"]["ai_review_summary"]

    # 9. List deployments
    res = await auth_client.get(f"/api/v1/dev/repos/{repo_id}/deployments")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 10. Link repo to project (create project first)
    proj_res = await auth_client.post(
        "/api/v1/projects",
        json={"name": "Dev Hub Test Project", "status": "active"},
    )
    project_id = proj_res.json()["data"]["id"]

    res = await auth_client.patch(
        f"/api/v1/dev/repos/{repo_id}",
        json={"project_id": project_id},
    )
    assert res.status_code == 200
    assert res.json()["data"]["project_id"] == project_id

    # 11. Encrypted env variable
    res = await auth_client.post(
        "/api/v1/dev/env",
        json={
            "repository_id": repo_id,
            "key": "DATABASE_URL",
            "value": "postgres://user:pass@localhost:5432/db",
            "environment": "production",
        },
    )
    assert res.status_code == 200
    env_id = res.json()["data"]["id"]

    res = await auth_client.get(f"/api/v1/dev/env?repo_id={repo_id}")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    res = await auth_client.delete(f"/api/v1/dev/env/{env_id}")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_github_webhook(auth_client: AsyncClient):
    # Link a repo for webhook target
    await auth_client.post(
        "/api/v1/dev/repos",
        json={
            "provider": "github",
            "external_repo_id": "wh_repo",
            "name": "webhook-repo",
            "full_name": "axorks/webhook-repo",
            "html_url": "https://github.com/axorks/webhook-repo",
        },
    )

    payload = {
        "action": "opened",
        "repository": {"full_name": "axorks/webhook-repo"},
        "pull_request": {
            "id": 555001,
            "number": 99,
            "title": "Webhook PR test",
            "state": "open",
            "html_url": "https://github.com/axorks/webhook-repo/pull/99",
            "user": {"login": "dev-bot"},
        },
    }

    res = await auth_client.post(
        "/api/v1/dev/webhooks/github",
        json=payload,
        headers={"X-GitHub-Event": "pull_request"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["handled"] is True
