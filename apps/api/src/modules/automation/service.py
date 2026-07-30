"""Axorks OS — Automation Service"""
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import NotFoundError
from src.modules.automation.executor import WorkflowExecutor
from src.modules.automation.models import Workflow, WorkflowExecution
from src.modules.automation.schemas import WorkflowCreate


class AutomationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow(self, org_id: UUID, ws_id: UUID, user_id: UUID, data: WorkflowCreate) -> Workflow:
        wf = Workflow(organization_id=org_id, workspace_id=ws_id, created_by=user_id, **data.model_dump())
        self.db.add(wf)
        await self.db.flush()
        await self.db.refresh(wf)
        return wf

    async def list_workflows(self, org_id: UUID) -> list[Workflow]:
        q = select(Workflow).where(Workflow.organization_id == org_id).order_by(Workflow.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def get_workflow(self, workflow_id: UUID, org_id: UUID) -> Workflow:
        res = await self.db.execute(select(Workflow).where(Workflow.id == workflow_id, Workflow.organization_id == org_id))
        wf = res.scalar_one_or_none()
        if not wf:
            raise NotFoundError("Workflow")
        return wf

    async def update_workflow(self, workflow_id: UUID, org_id: UUID, updates: dict) -> Workflow:
        wf = await self.get_workflow(workflow_id, org_id)
        for k, v in updates.items():
            if v is not None:
                setattr(wf, k, v)
        await self.db.flush()
        await self.db.refresh(wf)
        return wf

    async def toggle_workflow(self, workflow_id: UUID, org_id: UUID, is_active: bool) -> Workflow:
        wf = await self.get_workflow(workflow_id, org_id)
        wf.is_active = is_active
        await self.db.flush()
        await self.db.refresh(wf)
        return wf

    async def trigger_test_run(
        self, workflow_id: UUID, org_id: UUID, entity_type: str, entity_id: UUID | None, entity_data: dict
    ) -> WorkflowExecution:
        wf = await self.get_workflow(workflow_id, org_id)
        return await WorkflowExecutor.run_workflow(wf, entity_type, entity_id, entity_data, self.db)

    async def list_executions(self, workflow_id: UUID, org_id: UUID) -> list[WorkflowExecution]:
        await self.get_workflow(workflow_id, org_id)
        q = select(WorkflowExecution).where(WorkflowExecution.workflow_id == workflow_id).order_by(WorkflowExecution.started_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def get_execution_stats(self, org_id: UUID) -> dict:
        q_wfs = select(func.count()).select_from(Workflow).where(Workflow.organization_id == org_id)
        q_active = select(func.count()).select_from(Workflow).where(Workflow.organization_id == org_id, Workflow.is_active.is_(True))

        total_wfs = (await self.db.execute(q_wfs)).scalar_one()
        active_wfs = (await self.db.execute(q_active)).scalar_one()

        q_execs = select(func.count()).select_from(WorkflowExecution).join(Workflow).where(Workflow.organization_id == org_id)
        total_execs = (await self.db.execute(q_execs)).scalar_one()

        q_success = select(func.count()).select_from(WorkflowExecution).join(Workflow).where(
            Workflow.organization_id == org_id, WorkflowExecution.status == "success"
        )
        success_execs = (await self.db.execute(q_success)).scalar_one()

        success_rate = (success_execs / total_execs * 100) if total_execs > 0 else 100.0

        return {
            "total_workflows": total_wfs,
            "active_workflows": active_wfs,
            "total_executions": total_execs,
            "success_rate": round(success_rate, 2),
        }