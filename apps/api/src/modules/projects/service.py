"""
Axorks OS — Project Management Service
"""

from uuid import UUID
from datetime import UTC, datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.modules.projects.models import Project, Sprint, Task, TaskDependency, TimeEntry
from src.modules.projects.schemas import (
    ProjectCreate, ProjectUpdate, SprintCreate,
    TaskCreate, TaskUpdate, TimeEntryCreate,
)


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Projects ─────────────────────────────────────────────

    async def create_project(self, org_id: UUID, ws_id: UUID, data: ProjectCreate) -> Project:
        proj = Project(organization_id=org_id, workspace_id=ws_id, **data.model_dump())
        self.db.add(proj)
        await self.db.flush()
        await self.db.refresh(proj)
        return proj

    async def get_project(self, project_id: UUID, org_id: UUID) -> Project:
        q = select(Project).where(Project.id == project_id, Project.organization_id == org_id, Project.deleted_at.is_(None))
        res = await self.db.execute(q)
        proj = res.scalar_one_or_none()
        if not proj:
            raise NotFoundError("Project")
        return proj

    async def list_projects(self, org_id: UUID, page: int = 1, per_page: int = 25) -> tuple[list[Project], int]:
        q = select(Project).where(Project.organization_id == org_id, Project.deleted_at.is_(None))
        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        q = q.order_by(Project.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        items = list((await self.db.execute(q)).scalars().all())
        return items, total

    async def update_project(self, project_id: UUID, org_id: UUID, data: ProjectUpdate) -> Project:
        proj = await self.get_project(project_id, org_id)
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(proj, k, v)
        await self.db.flush()
        await self.db.refresh(proj)
        return proj

    async def delete_project(self, project_id: UUID, org_id: UUID) -> None:
        proj = await self.get_project(project_id, org_id)
        proj.deleted_at = datetime.now(UTC)
        await self.db.flush()

    # ── Sprints ──────────────────────────────────────────────

    async def create_sprint(self, data: SprintCreate) -> Sprint:
        sprint = Sprint(**data.model_dump())
        self.db.add(sprint)
        await self.db.flush()
        await self.db.refresh(sprint)
        return sprint

    async def list_sprints(self, project_id: UUID) -> list[Sprint]:
        q = select(Sprint).where(Sprint.project_id == project_id).order_by(Sprint.start_date.desc())
        return list((await self.db.execute(q)).scalars().all())

    # ── Tasks ────────────────────────────────────────────────

    async def create_task(self, org_id: UUID, ws_id: UUID, data: TaskCreate) -> Task:
        task = Task(organization_id=org_id, workspace_id=ws_id, **data.model_dump())
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def get_task(self, task_id: UUID, org_id: UUID) -> Task:
        q = select(Task).where(Task.id == task_id, Task.organization_id == org_id, Task.deleted_at.is_(None))
        res = await self.db.execute(q)
        t = res.scalar_one_or_none()
        if not t:
            raise NotFoundError("Task")
        return t

    async def list_tasks(self, org_id: UUID, project_id: UUID | None = None, status: str | None = None, sprint_id: UUID | None = None) -> list[Task]:
        q = select(Task).where(Task.organization_id == org_id, Task.deleted_at.is_(None))
        if project_id:
            q = q.where(Task.project_id == project_id)
        if sprint_id:
            q = q.where(Task.sprint_id == sprint_id)
        if status:
            q = q.where(Task.status == status)
        q = q.order_by(Task.sort_order, Task.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def update_task(self, task_id: UUID, org_id: UUID, data: TaskUpdate) -> Task:
        t = await self.get_task(task_id, org_id)
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(t, k, v)
        await self.db.flush()
        await self.db.refresh(t)
        return t

    async def delete_task(self, task_id: UUID, org_id: UUID) -> None:
        t = await self.get_task(task_id, org_id)
        t.deleted_at = datetime.now(UTC)
        await self.db.flush()

    # ── Time Entries ─────────────────────────────────────────

    async def log_time(self, org_id: UUID, user_id: UUID, data: TimeEntryCreate) -> TimeEntry:
        entry = TimeEntry(organization_id=org_id, user_id=user_id, **data.model_dump())
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def list_time_entries(self, org_id: UUID, project_id: UUID | None = None, task_id: UUID | None = None) -> list[TimeEntry]:
        q = select(TimeEntry).where(TimeEntry.organization_id == org_id)
        if project_id:
            q = q.where(TimeEntry.project_id == project_id)
        if task_id:
            q = q.where(TimeEntry.task_id == task_id)
        q = q.order_by(TimeEntry.logged_date.desc())
        return list((await self.db.execute(q)).scalars().all())
