"""
Axorks OS — Development Hub Schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class VCSIntegrationConnect(BaseModel):
    provider: str  # github, gitlab, bitbucket
    access_token: str
    refresh_token: str | None = None
    account_username: str | None = None


class VCSIntegrationRead(BaseModel):
    id: UUID
    organization_id: UUID
    provider: str
    account_username: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GitHubOAuthCallback(BaseModel):
    code: str
    state: str | None = None


class RemoteRepositoryRead(BaseModel):
    external_repo_id: str
    name: str
    full_name: str
    html_url: str | None = None
    default_branch: str = "main"
    is_private: bool = True
    provider: str


class RepositoryConnect(BaseModel):
    provider: str
    external_repo_id: str
    name: str
    full_name: str
    html_url: str | None = None
    default_branch: str = "main"
    is_private: bool = True
    project_id: UUID | None = None


class RepositoryUpdate(BaseModel):
    project_id: UUID | None = None
    default_branch: str | None = None


class RepositoryRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    project_id: UUID | None = None
    provider: str
    external_repo_id: str
    name: str
    full_name: str
    html_url: str | None = None
    default_branch: str
    is_private: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PullRequestRead(BaseModel):
    id: UUID
    repository_id: UUID
    external_pr_id: str
    number: int
    title: str
    state: str
    author: str | None = None
    html_url: str | None = None
    ai_review_summary: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class IssueRead(BaseModel):
    id: UUID
    repository_id: UUID
    external_issue_id: str
    number: int
    title: str
    state: str
    author: str | None = None
    labels: str | None = None
    html_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DeploymentRead(BaseModel):
    id: UUID
    repository_id: UUID
    environment: str
    status: str
    commit_hash: str | None = None
    url: str | None = None
    deployed_at: datetime

    model_config = {"from_attributes": True}


class EnvVariableCreate(BaseModel):
    repository_id: UUID | None = None
    environment: str = "production"
    key: str
    value: str


class EnvVariableRead(BaseModel):
    id: UUID
    organization_id: UUID
    repository_id: UUID | None = None
    environment: str
    key: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncResult(BaseModel):
    pull_requests: int = 0
    issues: int = 0
    deployments: int = 0
    message: str = "Sync completed"
