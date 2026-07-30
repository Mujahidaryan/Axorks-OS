"""
Axorks OS — GitHub API Client

Syncs repositories, pull requests, issues, and deployments from GitHub.
"""

from __future__ import annotations

from typing import Any

import httpx


class GitHubClient:
    """Minimal GitHub REST API client for Development Hub sync."""

    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @property
    def is_configured(self) -> bool:
        token = (self.access_token or "").strip()
        return bool(token) and not token.startswith("mock_")

    async def _get(self, path: str, params: dict | None = None) -> Any:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.BASE_URL}{path}",
                headers=self.headers,
                params=params or {},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_authenticated_user(self) -> dict:
        return await self._get("/user")

    async def list_repos(self, per_page: int = 30) -> list[dict]:
        return await self._get("/user/repos", {"per_page": per_page, "sort": "updated"})

    async def list_pulls(self, owner: str, repo: str, state: str = "all") -> list[dict]:
        return await self._get(f"/repos/{owner}/{repo}/pulls", {"state": state, "per_page": 50})

    async def list_issues(self, owner: str, repo: str, state: str = "open") -> list[dict]:
        issues = await self._get(f"/repos/{owner}/{repo}/issues", {"state": state, "per_page": 50})
        return [i for i in issues if "pull_request" not in i]

    async def list_deployments(self, owner: str, repo: str) -> list[dict]:
        return await self._get(f"/repos/{owner}/{repo}/deployments", {"per_page": 20})

    @staticmethod
    async def exchange_oauth_code(
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str,
    ) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                json={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
            resp.raise_for_status()
            return resp.json()
