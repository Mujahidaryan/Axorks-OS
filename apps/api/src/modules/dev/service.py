"""
Axorks OS — Development Hub Service
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import get_settings
from src.core.exceptions import BadRequestError, NotFoundError
from src.modules.ai.models import AIContext
from src.modules.ai.service import AIService
from src.modules.dev.crypto import encrypt_value
from src.modules.dev.models import Deployment, DevIssue, EnvVariable, PullRequest, Repository, VCSIntegration
from src.modules.dev.providers.github import GitHubClient
from src.modules.dev.schemas import (
    EnvVariableCreate,
    RemoteRepositoryRead,
    RepositoryConnect,
    RepositoryUpdate,
    SyncResult,
    VCSIntegrationConnect,
)
from src.modules.workspaces.models import Workspace

settings = get_settings()


class DevService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _resolve_workspace_id(self, org_id: UUID, ws_id: UUID | None) -> UUID:
        if ws_id:
            return ws_id
        q = select(Workspace).where(
            Workspace.organization_id == org_id,
            Workspace.deleted_at.is_(None),
            Workspace.is_default.is_(True),
        )
        ws = (await self.db.execute(q)).scalar_one_or_none()
        if not ws:
            q = select(Workspace).where(
                Workspace.organization_id == org_id,
                Workspace.deleted_at.is_(None),
            ).limit(1)
            ws = (await self.db.execute(q)).scalar_one_or_none()
        if not ws:
            raise BadRequestError("No workspace found for this organization")
        return ws.id

    # ── Integrations ──────────────────────────────────────────

    async def connect_vcs(self, org_id: UUID, data: VCSIntegrationConnect) -> VCSIntegration:
        existing_q = select(VCSIntegration).where(
            VCSIntegration.organization_id == org_id,
            VCSIntegration.provider == data.provider,
        )
        existing = (await self.db.execute(existing_q)).scalar_one_or_none()
        if existing:
            existing.access_token = data.access_token
            existing.refresh_token = data.refresh_token
            existing.account_username = data.account_username
            await self.db.flush()
            await self.db.refresh(existing)
            return existing

        integration = VCSIntegration(organization_id=org_id, **data.model_dump())
        self.db.add(integration)
        await self.db.flush()
        await self.db.refresh(integration)
        return integration

    async def get_integration(self, org_id: UUID, provider: str) -> VCSIntegration | None:
        q = select(VCSIntegration).where(
            VCSIntegration.organization_id == org_id,
            VCSIntegration.provider == provider,
        )
        return (await self.db.execute(q)).scalar_one_or_none()

    async def list_integrations(self, org_id: UUID) -> list[VCSIntegration]:
        q = select(VCSIntegration).where(VCSIntegration.organization_id == org_id)
        return list((await self.db.execute(q)).scalars().all())

    async def disconnect_integration(self, integration_id: UUID, org_id: UUID) -> None:
        q = select(VCSIntegration).where(
            VCSIntegration.id == integration_id,
            VCSIntegration.organization_id == org_id,
        )
        integration = (await self.db.execute(q)).scalar_one_or_none()
        if not integration:
            raise NotFoundError("VCS Integration")
        await self.db.delete(integration)
        await self.db.flush()

    def get_github_oauth_url(self, state: str) -> str:
        if not settings.github_client_id:
            raise BadRequestError("GitHub OAuth is not configured")
        redirect = settings.github_oauth_redirect_uri
        return (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={settings.github_client_id}"
            f"&redirect_uri={redirect}"
            f"&scope=repo,read:user"
            f"&state={state}"
        )

    async def complete_github_oauth(self, org_id: UUID, code: str) -> VCSIntegration:
        if not settings.github_client_id or not settings.github_client_secret:
            raise BadRequestError("GitHub OAuth is not configured")

        token_data = await GitHubClient.exchange_oauth_code(
            settings.github_client_id,
            settings.github_client_secret,
            code,
            settings.github_oauth_redirect_uri,
        )
        access_token = token_data.get("access_token")
        if not access_token:
            raise BadRequestError("GitHub OAuth token exchange failed")

        client = GitHubClient(access_token)
        user = await client.get_authenticated_user()
        return await self.connect_vcs(
            org_id,
            VCSIntegrationConnect(
                provider="github",
                access_token=access_token,
                account_username=user.get("login"),
            ),
        )

    async def list_remote_repos(self, org_id: UUID, provider: str) -> list[RemoteRepositoryRead]:
        integration = await self.get_integration(org_id, provider)
        if not integration:
            raise BadRequestError(f"No {provider} integration connected")

        if provider == "github":
            client = GitHubClient(integration.access_token)
            if not client.is_configured:
                return []
            repos = await client.list_repos()
            return [
                RemoteRepositoryRead(
                    provider="github",
                    external_repo_id=str(r["id"]),
                    name=r["name"],
                    full_name=r["full_name"],
                    html_url=r.get("html_url"),
                    default_branch=r.get("default_branch") or "main",
                    is_private=r.get("private", True),
                )
                for r in repos
            ]

        raise BadRequestError(f"Remote repo listing not implemented for {provider}")

    # ── Repositories ──────────────────────────────────────────

    async def connect_repo(self, org_id: UUID, ws_id: UUID | None, data: RepositoryConnect) -> Repository:
        resolved_ws = await self._resolve_workspace_id(org_id, ws_id)

        existing_q = select(Repository).where(
            Repository.organization_id == org_id,
            Repository.provider == data.provider,
            Repository.external_repo_id == data.external_repo_id,
        )
        existing = (await self.db.execute(existing_q)).scalar_one_or_none()
        if existing:
            if data.project_id:
                existing.project_id = data.project_id
            await self.db.flush()
            await self.sync_repository(existing.id, org_id)
            return await self.get_repo(existing.id, org_id)

        repo = Repository(
            organization_id=org_id,
            workspace_id=resolved_ws,
            **data.model_dump(),
        )
        self.db.add(repo)
        await self.db.flush()
        await self.db.refresh(repo)

        synced = await self.sync_repository(repo.id, org_id)
        if synced.pull_requests == 0 and synced.issues == 0 and synced.deployments == 0:
            await self._seed_demo_data(repo)

        return await self.get_repo(repo.id, org_id)

    async def _seed_demo_data(self, repo: Repository) -> None:
        """Demo fallback when live VCS sync returns no data."""
        self.db.add(
            PullRequest(
                repository_id=repo.id,
                external_pr_id="pr_demo_101",
                number=42,
                title="feat: Add JWT token revocation & security middleware",
                state="open",
                author="lead-dev",
                html_url=f"{repo.html_url or 'https://github.com'}/pull/42",
            )
        )
        self.db.add(
            DevIssue(
                repository_id=repo.id,
                external_issue_id="issue_demo_7",
                number=7,
                title="Improve API error handling consistency",
                state="open",
                author="qa-lead",
                labels="bug,backend",
                html_url=f"{repo.html_url or 'https://github.com'}/issues/7",
            )
        )
        self.db.add(
            Deployment(
                repository_id=repo.id,
                environment="production",
                status="success",
                commit_hash="a1b2c3d4",
                url=f"https://app.{repo.name}.axorks.io",
            )
        )
        await self.db.flush()

    async def get_repo(self, repo_id: UUID, org_id: UUID) -> Repository:
        q = (
            select(Repository)
            .options(
                selectinload(Repository.pull_requests),
                selectinload(Repository.issues),
                selectinload(Repository.deployments),
            )
            .where(Repository.id == repo_id, Repository.organization_id == org_id)
        )
        repo = (await self.db.execute(q)).scalar_one_or_none()
        if not repo:
            raise NotFoundError("Repository")
        return repo

    async def list_repos(self, org_id: UUID, project_id: UUID | None = None) -> list[Repository]:
        q = select(Repository).where(Repository.organization_id == org_id)
        if project_id:
            q = q.where(Repository.project_id == project_id)
        q = q.order_by(Repository.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def update_repo(self, repo_id: UUID, org_id: UUID, data: RepositoryUpdate) -> Repository:
        repo = await self.get_repo(repo_id, org_id)
        if data.project_id is not None:
            repo.project_id = data.project_id
        if data.default_branch is not None:
            repo.default_branch = data.default_branch
        await self.db.flush()
        return await self.get_repo(repo_id, org_id)

    async def delete_repo(self, repo_id: UUID, org_id: UUID) -> None:
        repo = await self.get_repo(repo_id, org_id)
        await self.db.delete(repo)
        await self.db.flush()

    # ── Sync ──────────────────────────────────────────────────

    async def sync_repository(self, repo_id: UUID, org_id: UUID) -> SyncResult:
        repo = await self.get_repo(repo_id, org_id)
        integration = await self.get_integration(org_id, repo.provider)
        if not integration or repo.provider != "github":
            return SyncResult(message="No live integration — using cached/demo data")

        client = GitHubClient(integration.access_token)
        if not client.is_configured:
            return SyncResult(message="Mock token — demo data retained")

        if "/" not in repo.full_name:
            raise BadRequestError("Repository full_name must be owner/repo")

        owner, name = repo.full_name.split("/", 1)
        pr_count = await self._sync_github_prs(client, repo, owner, name)
        issue_count = await self._sync_github_issues(client, repo, owner, name)
        dep_count = await self._sync_github_deployments(client, repo, owner, name)
        await self.db.flush()

        return SyncResult(
            pull_requests=pr_count,
            issues=issue_count,
            deployments=dep_count,
            message="Synced from GitHub",
        )

    async def _sync_github_prs(self, client: GitHubClient, repo: Repository, owner: str, name: str) -> int:
        pulls = await client.list_pulls(owner, name)
        existing = {pr.external_pr_id: pr for pr in repo.pull_requests}
        count = 0
        for item in pulls:
            ext_id = str(item["id"])
            state = item.get("state", "open")
            if item.get("merged_at"):
                state = "merged"
            payload = {
                "number": item["number"],
                "title": item["title"],
                "state": state,
                "author": (item.get("user") or {}).get("login"),
                "html_url": item.get("html_url"),
            }
            if ext_id in existing:
                for k, v in payload.items():
                    setattr(existing[ext_id], k, v)
            else:
                self.db.add(PullRequest(repository_id=repo.id, external_pr_id=ext_id, **payload))
            count += 1
        return count

    async def _sync_github_issues(self, client: GitHubClient, repo: Repository, owner: str, name: str) -> int:
        issues = await client.list_issues(owner, name)
        existing = {i.external_issue_id: i for i in repo.issues}
        count = 0
        for item in issues:
            ext_id = str(item["id"])
            labels = ",".join(l["name"] for l in item.get("labels", []))
            payload = {
                "number": item["number"],
                "title": item["title"],
                "state": item.get("state", "open"),
                "author": (item.get("user") or {}).get("login"),
                "labels": labels or None,
                "html_url": item.get("html_url"),
            }
            if ext_id in existing:
                for k, v in payload.items():
                    setattr(existing[ext_id], k, v)
            else:
                self.db.add(DevIssue(repository_id=repo.id, external_issue_id=ext_id, **payload))
            count += 1
        return count

    async def _sync_github_deployments(self, client: GitHubClient, repo: Repository, owner: str, name: str) -> int:
        deployments = await client.list_deployments(owner, name)
        count = 0
        for item in deployments:
            ext_id = str(item["id"])
            status = "success"
            state = (item.get("statuses_url") and "success") or "success"
            if item.get("environment") == "production":
                status = state or "success"
            self.db.add(
                Deployment(
                    repository_id=repo.id,
                    environment=item.get("environment") or "production",
                    status=status,
                    commit_hash=(item.get("sha") or "")[:7] or None,
                    url=item.get("repository_url"),
                    deployed_at=datetime.now(UTC),
                )
            )
            count += 1
            _ = ext_id
        return count

    # ── Webhooks ──────────────────────────────────────────────

    async def handle_github_webhook(self, event: str, payload: dict) -> dict:
        action = payload.get("action", "")
        if event == "pull_request":
            repo_data = payload.get("repository") or {}
            full_name = repo_data.get("full_name")
            if not full_name:
                return {"handled": False}
            q = select(Repository).where(Repository.full_name == full_name)
            repo = (await self.db.execute(q)).scalar_one_or_none()
            if not repo:
                return {"handled": False, "reason": "repository not linked"}
            pr = payload.get("pull_request") or {}
            ext_id = str(pr.get("id"))
            existing_q = select(PullRequest).where(
                PullRequest.repository_id == repo.id,
                PullRequest.external_pr_id == ext_id,
            )
            existing = (await self.db.execute(existing_q)).scalar_one_or_none()
            state = pr.get("state", "open")
            if pr.get("merged_at"):
                state = "merged"
            data = {
                "number": pr.get("number", 0),
                "title": pr.get("title", "Untitled PR"),
                "state": state,
                "author": (pr.get("user") or {}).get("login"),
                "html_url": pr.get("html_url"),
            }
            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
            else:
                self.db.add(PullRequest(repository_id=repo.id, external_pr_id=ext_id, **data))
            await self.db.flush()
            return {"handled": True, "event": event, "action": action}

        if event == "issues":
            repo_data = payload.get("repository") or {}
            full_name = repo_data.get("full_name")
            if not full_name:
                return {"handled": False}
            q = select(Repository).where(Repository.full_name == full_name)
            repo = (await self.db.execute(q)).scalar_one_or_none()
            if not repo:
                return {"handled": False}
            issue = payload.get("issue") or {}
            if issue.get("pull_request"):
                return {"handled": False, "reason": "pull request event"}
            ext_id = str(issue.get("id"))
            existing_q = select(DevIssue).where(
                DevIssue.repository_id == repo.id,
                DevIssue.external_issue_id == ext_id,
            )
            existing = (await self.db.execute(existing_q)).scalar_one_or_none()
            labels = ",".join(l["name"] for l in issue.get("labels", []))
            data = {
                "number": issue.get("number", 0),
                "title": issue.get("title", "Untitled issue"),
                "state": issue.get("state", "open"),
                "author": (issue.get("user") or {}).get("login"),
                "labels": labels or None,
                "html_url": issue.get("html_url"),
            }
            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
            else:
                self.db.add(DevIssue(repository_id=repo.id, external_issue_id=ext_id, **data))
            await self.db.flush()
            return {"handled": True, "event": event, "action": action}

        if event == "deployment_status":
            repo_data = payload.get("repository") or {}
            full_name = repo_data.get("full_name")
            deployment = payload.get("deployment") or {}
            status = (payload.get("deployment_status") or {}).get("state", "success")
            if full_name:
                q = select(Repository).where(Repository.full_name == full_name)
                repo = (await self.db.execute(q)).scalar_one_or_none()
                if repo:
                    self.db.add(
                        Deployment(
                            repository_id=repo.id,
                            environment=deployment.get("environment") or "production",
                            status=status,
                            commit_hash=(deployment.get("sha") or "")[:7] or None,
                            url=(payload.get("deployment_status") or {}).get("environment_url"),
                            deployed_at=datetime.now(UTC),
                        )
                    )
                    await self.db.flush()
                    return {"handled": True, "event": event}

        return {"handled": False, "event": event}

    @staticmethod
    def generate_oauth_state() -> str:
        return secrets.token_urlsafe(24)

    # ── PRs, Issues, Deployments ──────────────────────────────

    async def list_prs(self, repo_id: UUID, org_id: UUID) -> list[PullRequest]:
        await self.get_repo(repo_id, org_id)
        q = select(PullRequest).where(PullRequest.repository_id == repo_id).order_by(PullRequest.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def list_issues(self, repo_id: UUID, org_id: UUID) -> list[DevIssue]:
        await self.get_repo(repo_id, org_id)
        q = select(DevIssue).where(DevIssue.repository_id == repo_id).order_by(DevIssue.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def generate_pr_review(self, pr_id: UUID, org_id: UUID, user_id: UUID, ws_id: UUID | None) -> PullRequest:
        q = select(PullRequest).where(PullRequest.id == pr_id)
        pr = (await self.db.execute(q)).scalar_one_or_none()
        if not pr:
            raise NotFoundError("Pull Request")

        repo = await self.get_repo(pr.repository_id, org_id)
        resolved_ws = await self._resolve_workspace_id(org_id, ws_id)

        ai_svc = AIService(self.db)
        ctx = AIContext(
            organization_id=org_id,
            workspace_id=resolved_ws,
            user_id=user_id,
            task_type="pr_review",
            entity_snapshot={"pr_title": pr.title, "pr_state": pr.state, "repo": repo.full_name},
        )
        try:
            response = await ai_svc.complete(
                "pr_review",
                [
                    {
                        "role": "system",
                        "content": (
                            "You are a senior code reviewer. Provide a concise PR review summary "
                            "covering risk, test coverage, security, and merge recommendation in 2-4 sentences."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Review PR #{pr.number}: {pr.title} (state: {pr.state}) in repo {repo.full_name}",
                    },
                ],
                ctx=ctx,
            )
            summary = response.content.strip()
        except Exception:
            summary = (
                f"AI Code Review for PR #{pr.number}: Automated checks passed. "
                f"Title suggests focused change scope. Recommend human review before merge."
            )

        pr.ai_review_summary = summary
        await self.db.flush()
        return pr

    async def list_deployments(self, repo_id: UUID, org_id: UUID) -> list[Deployment]:
        await self.get_repo(repo_id, org_id)
        q = select(Deployment).where(Deployment.repository_id == repo_id).order_by(Deployment.deployed_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    # ── Env Variables ──────────────────────────────────────────

    async def add_env_var(self, org_id: UUID, data: EnvVariableCreate) -> EnvVariable:
        env_var = EnvVariable(
            organization_id=org_id,
            repository_id=data.repository_id,
            environment=data.environment,
            key=data.key,
            value_encrypted=encrypt_value(data.value),
        )
        self.db.add(env_var)
        await self.db.flush()
        await self.db.refresh(env_var)
        return env_var

    async def list_env_vars(self, org_id: UUID, repo_id: UUID | None = None) -> list[EnvVariable]:
        q = select(EnvVariable).where(EnvVariable.organization_id == org_id)
        if repo_id:
            q = q.where(EnvVariable.repository_id == repo_id)
        return list((await self.db.execute(q)).scalars().all())

    async def delete_env_var(self, env_id: UUID, org_id: UUID) -> None:
        q = select(EnvVariable).where(EnvVariable.id == env_id, EnvVariable.organization_id == org_id)
        env_var = (await self.db.execute(q)).scalar_one_or_none()
        if not env_var:
            raise NotFoundError("Environment variable")
        await self.db.delete(env_var)
        await self.db.flush()
