"""
Axorks OS — Development Hub API Router
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.permissions import require_permission
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.dev.schemas import (
    DeploymentRead,
    EnvVariableCreate,
    EnvVariableRead,
    GitHubOAuthCallback,
    IssueRead,
    PullRequestRead,
    RemoteRepositoryRead,
    RepositoryConnect,
    RepositoryRead,
    RepositoryUpdate,
    SyncResult,
    VCSIntegrationConnect,
    VCSIntegrationRead,
)
from src.modules.dev.service import DevService

router = APIRouter(prefix="/api/v1/dev", tags=["Development Hub"])
settings = get_settings()


@router.post("/integrations/vcs")
@require_permission("dev:write")
async def connect_vcs(
    data: VCSIntegrationConnect,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    i = await svc.connect_vcs(ctx.org_id, data)
    return success_response(data=VCSIntegrationRead.model_validate(i).model_dump(mode="json"))


@router.get("/integrations/vcs")
@require_permission("dev:read")
async def list_integrations(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    items = await svc.list_integrations(ctx.org_id)
    return success_response(data=[VCSIntegrationRead.model_validate(i).model_dump(mode="json") for i in items])


@router.delete("/integrations/vcs/{integration_id}")
@require_permission("dev:write")
async def disconnect_integration(
    integration_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    await svc.disconnect_integration(integration_id, ctx.org_id)
    return success_response(data={"message": "Integration disconnected"})


@router.get("/oauth/github/authorize")
@require_permission("dev:write")
async def github_oauth_authorize(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    state = svc.generate_oauth_state()
    url = svc.get_github_oauth_url(state)
    return success_response(data={"url": url, "state": state})


@router.post("/oauth/github/callback")
@require_permission("dev:write")
async def github_oauth_callback(
    data: GitHubOAuthCallback,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    integration = await svc.complete_github_oauth(ctx.org_id, data.code)
    return success_response(data=VCSIntegrationRead.model_validate(integration).model_dump(mode="json"))


@router.get("/integrations/vcs/{provider}/remote-repos")
@require_permission("dev:read")
async def list_remote_repos(
    provider: str,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    repos = await svc.list_remote_repos(ctx.org_id, provider)
    return success_response(data=[RemoteRepositoryRead.model_dump(mode="json") for r in repos])


@router.post("/repos")
@require_permission("dev:write")
async def connect_repo(
    data: RepositoryConnect,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    repo = await svc.connect_repo(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=RepositoryRead.model_validate(repo).model_dump(mode="json"))


@router.get("/repos")
@require_permission("dev:read")
async def list_repos(
    project_id: UUID | None = None,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    repos = await svc.list_repos(ctx.org_id, project_id)
    return success_response(data=[RepositoryRead.model_validate(r).model_dump(mode="json") for r in repos])


@router.get("/repos/{repo_id}")
@require_permission("dev:read")
async def get_repo(
    repo_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    repo = await svc.get_repo(repo_id, ctx.org_id)
    return success_response(data=RepositoryRead.model_validate(repo).model_dump(mode="json"))


@router.patch("/repos/{repo_id}")
@require_permission("dev:write")
async def update_repo(
    repo_id: UUID,
    data: RepositoryUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    repo = await svc.update_repo(repo_id, ctx.org_id, data)
    return success_response(data=RepositoryRead.model_validate(repo).model_dump(mode="json"))


@router.delete("/repos/{repo_id}")
@require_permission("dev:write")
async def delete_repo(
    repo_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    await svc.delete_repo(repo_id, ctx.org_id)
    return success_response(data={"message": "Repository unlinked"})


@router.post("/repos/{repo_id}/sync")
@require_permission("dev:write")
async def sync_repo(
    repo_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    result = await svc.sync_repository(repo_id, ctx.org_id)
    return success_response(data=SyncResult.model_validate(result).model_dump(mode="json"))


@router.get("/repos/{repo_id}/prs")
@require_permission("dev:read")
async def list_prs(
    repo_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    prs = await svc.list_prs(repo_id, ctx.org_id)
    return success_response(data=[PullRequestRead.model_validate(p).model_dump(mode="json") for p in prs])


@router.get("/repos/{repo_id}/issues")
@require_permission("dev:read")
async def list_issues(
    repo_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    issues = await svc.list_issues(repo_id, ctx.org_id)
    return success_response(data=[IssueRead.model_validate(i).model_dump(mode="json") for i in issues])


@router.post("/prs/{pr_id}/ai-review")
@require_permission("dev:write")
async def generate_pr_review(
    pr_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    pr = await svc.generate_pr_review(pr_id, ctx.org_id, ctx.user_id, ctx.workspace_id)
    return success_response(data=PullRequestRead.model_validate(pr).model_dump(mode="json"))


@router.get("/repos/{repo_id}/deployments")
@require_permission("dev:read")
async def list_deployments(
    repo_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    deps = await svc.list_deployments(repo_id, ctx.org_id)
    return success_response(data=[DeploymentRead.model_validate(d).model_dump(mode="json") for d in deps])


@router.post("/env")
@require_permission("dev:write")
async def add_env_var(
    data: EnvVariableCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    ev = await svc.add_env_var(ctx.org_id, data)
    return success_response(data=EnvVariableRead.model_validate(ev).model_dump(mode="json"))


@router.get("/env")
@require_permission("dev:read")
async def list_env_vars(
    repo_id: UUID | None = None,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    vars_list = await svc.list_env_vars(ctx.org_id, repo_id)
    return success_response(data=[EnvVariableRead.model_validate(v).model_dump(mode="json") for v in vars_list])


@router.delete("/env/{env_id}")
@require_permission("dev:write")
async def delete_env_var(
    env_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    svc = DevService(db)
    await svc.delete_env_var(env_id, ctx.org_id)
    return success_response(data={"message": "Environment variable deleted"})


@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_github_event: str | None = Header(default=None, alias="X-GitHub-Event"),
):
    """Public webhook receiver for GitHub PR, issue, and deployment events."""
    import hashlib
    import hmac
    import json

    body = await request.body()

    if settings.github_webhook_secret:
        signature = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(
            settings.github_webhook_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return success_response(data={"handled": False, "reason": "invalid signature"})

    payload = json.loads(body)
    svc = DevService(db)
    result = await svc.handle_github_webhook(x_github_event or "", payload)
    return success_response(data=result)
