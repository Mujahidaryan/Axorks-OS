"""Axorks OS — Automation Engine Router"""
from uuid import UUID
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.automation.schemas import TestTriggerRequest, WorkflowCreate, WorkflowExecutionRead, WorkflowRead
from src.modules.automation.service import AutomationService

router = APIRouter(prefix="/api/v1/automations", tags=["Automation Engine"])


@router.post("/workflows")
async def create_workflow(data: WorkflowCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AutomationService(db)
    wf = await svc.create_workflow(ctx.org_id, ctx.workspace_id, ctx.user_id, data)
    return success_response(data=WorkflowRead.model_validate(wf).model_dump(mode="json"))


@router.get("/workflows")
async def list_workflows(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AutomationService(db)
    workflows = await svc.list_workflows(ctx.org_id)
    return success_response(data=[WorkflowRead.model_validate(w).model_dump(mode="json") for w in workflows])


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AutomationService(db)
    wf = await svc.get_workflow(workflow_id, ctx.org_id)
    return success_response(data=WorkflowRead.model_validate(wf).model_dump(mode="json"))


@router.patch("/workflows/{workflow_id}")
async def update_workflow(workflow_id: UUID, updates: dict, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AutomationService(db)
    wf = await svc.update_workflow(workflow_id, ctx.org_id, updates)
    return success_response(data=WorkflowRead.model_validate(wf).model_dump(mode="json"))


@router.post("/workflows/{workflow_id}/toggle")
async def toggle_workflow(workflow_id: UUID, is_active: bool = Body(..., embed=True), ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AutomationService(db)
    wf = await svc.toggle_workflow(workflow_id, ctx.org_id, is_active)
    return success_response(data=WorkflowRead.model_validate(wf).model_dump(mode="json"))


@router.post("/workflows/{workflow_id}/test-trigger")
async def test_trigger(workflow_id: UUID, req: TestTriggerRequest, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AutomationService(db)
    execution = await svc.trigger_test_run(workflow_id, ctx.org_id, req.entity_type, req.entity_id, req.entity_data)
    return success_response(data=WorkflowExecutionRead.model_validate(execution).model_dump(mode="json"))


@router.get("/workflows/{workflow_id}/executions")
async def list_executions(workflow_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AutomationService(db)
    executions = await svc.list_executions(workflow_id, ctx.org_id)
    return success_response(data=[WorkflowExecutionRead.model_validate(e).model_dump(mode="json") for e in executions])


@router.get("/stats")
async def get_stats(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AutomationService(db)
    stats = await svc.get_execution_stats(ctx.org_id)
    return success_response(data=stats)