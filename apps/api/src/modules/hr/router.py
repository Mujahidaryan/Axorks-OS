"""Axorks OS — HR Router"""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.hr.schemas import EmployeeCreate, EmployeeRead, LeaveRequestCreate, LeaveRequestRead, PerformanceReviewCreate, PerformanceReviewRead
from src.modules.hr.service import HRService

router = APIRouter(prefix="/api/v1/hr", tags=["HR"])


@router.post("/employees")
async def create_employee(data: EmployeeCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    emp = await svc.create_employee(ctx.org_id, data)
    return success_response(data=EmployeeRead.model_validate(emp).model_dump(mode="json"))


@router.get("/employees")
async def list_employees(department: str | None = None, status: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    employees = await svc.list_employees(ctx.org_id, department, status)
    return success_response(data=[EmployeeRead.model_validate(e).model_dump(mode="json") for e in employees])


@router.get("/employees/{employee_id}")
async def get_employee(employee_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    emp = await svc.get_employee(employee_id, ctx.org_id)
    return success_response(data=EmployeeRead.model_validate(emp).model_dump(mode="json"))


@router.patch("/employees/{employee_id}")
async def update_employee(employee_id: UUID, updates: dict, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    emp = await svc.update_employee(employee_id, ctx.org_id, updates)
    return success_response(data=EmployeeRead.model_validate(emp).model_dump(mode="json"))


@router.post("/leave-requests")
async def request_leave(data: LeaveRequestCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    req = await svc.request_leave(ctx.org_id, data)
    return success_response(data=LeaveRequestRead.model_validate(req).model_dump(mode="json"))


@router.get("/leave-requests")
async def list_leave_requests(status: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    requests = await svc.list_leave_requests(ctx.org_id, status)
    return success_response(data=[LeaveRequestRead.model_validate(r).model_dump(mode="json") for r in requests])


@router.post("/leave-requests/{request_id}/approve")
async def approve_leave(request_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    req = await svc.approve_leave(request_id, ctx.org_id, ctx.user_id)
    return success_response(data=LeaveRequestRead.model_validate(req).model_dump(mode="json"))


@router.post("/leave-requests/{request_id}/reject")
async def reject_leave(request_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    req = await svc.reject_leave(request_id, ctx.org_id)
    return success_response(data=LeaveRequestRead.model_validate(req).model_dump(mode="json"))


@router.post("/performance-reviews")
async def create_review(data: PerformanceReviewCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    review = await svc.create_review(ctx.org_id, data)
    return success_response(data=PerformanceReviewRead.model_validate(review).model_dump(mode="json"))


@router.get("/performance-reviews")
async def list_reviews(employee_id: UUID | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    reviews = await svc.list_reviews(ctx.org_id, employee_id)
    return success_response(data=[PerformanceReviewRead.model_validate(r).model_dump(mode="json") for r in reviews])


@router.get("/stats/headcount")
async def get_headcount_stats(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = HRService(db)
    stats = await svc.get_headcount_stats(ctx.org_id)
    return success_response(data=stats)