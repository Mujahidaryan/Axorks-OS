"""
Axorks OS — Project Management API Router
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import paginated_response, success_response
from src.core.tenant import TenantContext
from src.modules.projects.schemas import (
    ProjectCreate, ProjectRead, ProjectUpdate,
    SprintCreate, SprintRead,
    TaskCreate, TaskRead, TaskUpdate,
    TimeEntryCreate, TimeEntryRead,
)
from src.modules.projects.service import ProjectService

router = APIRouter(prefix="/api/v1/projects", tags=["Project Management"])


# ── Projects ─────────────────────────────────────────────

@router.post("")
async def create_project(data: ProjectCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    proj = await svc.create_project(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=ProjectRead.model_validate(proj).model_dump(mode="json"))


@router.get("")
async def list_projects(page: int = Query(1, ge=1), per_page: int = Query(25), ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    items, total = await svc.list_projects(ctx.org_id, page, per_page)
    return paginated_response([ProjectRead.model_validate(i).model_dump(mode="json") for i in items], page, per_page, total)


@router.get("/{project_id}")
async def get_project(project_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    proj = await svc.get_project(project_id, ctx.org_id)
    return success_response(data=ProjectRead.model_validate(proj).model_dump(mode="json"))


@router.patch("/{project_id}")
async def update_project(project_id: UUID, data: ProjectUpdate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    proj = await svc.update_project(project_id, ctx.org_id, data)
    return success_response(data=ProjectRead.model_validate(proj).model_dump(mode="json"))


@router.delete("/{project_id}")
async def delete_project(project_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    await svc.delete_project(project_id, ctx.org_id)
    return success_response(data={"message": "Project deleted"})


# ── Sprints ──────────────────────────────────────────────

@router.post("/sprints")
async def create_sprint(data: SprintCreate, db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    sprint = await svc.create_sprint(data)
    return success_response(data=SprintRead.model_validate(sprint).model_dump(mode="json"))


@router.get("/{project_id}/sprints")
async def list_sprints(project_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    items = await svc.list_sprints(project_id)
    return success_response(data=[SprintRead.model_validate(i).model_dump(mode="json") for i in items])


# ── Tasks ────────────────────────────────────────────────

@router.post("/tasks")
async def create_task(data: TaskCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    t = await svc.create_task(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=TaskRead.model_validate(t).model_dump(mode="json"))


@router.get("/tasks")
async def list_tasks(project_id: UUID | None = None, sprint_id: UUID | None = None, status: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    items = await svc.list_tasks(ctx.org_id, project_id, status, sprint_id)
    return success_response(data=[TaskRead.model_validate(i).model_dump(mode="json") for i in items])


@router.patch("/tasks/{task_id}")
async def update_task(task_id: UUID, data: TaskUpdate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    t = await svc.update_task(task_id, ctx.org_id, data)
    return success_response(data=TaskRead.model_validate(t).model_dump(mode="json"))


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    await svc.delete_task(task_id, ctx.org_id)
    return success_response(data={"message": "Task deleted"})


# ── Time Entries ─────────────────────────────────────────

@router.post("/time")
async def log_time(data: TimeEntryCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    entry = await svc.log_time(ctx.org_id, ctx.user_id, data)
    return success_response(data=TimeEntryRead.model_validate(entry).model_dump(mode="json"))


@router.get("/time")
async def list_time(project_id: UUID | None = None, task_id: UUID | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = ProjectService(db)
    entries = await svc.list_time_entries(ctx.org_id, project_id, task_id)
    return success_response(data=[TimeEntryRead.model_validate(e).model_dump(mode="json") for e in entries])
