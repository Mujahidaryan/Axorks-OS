"""Axorks OS — HR Service"""
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import NotFoundError
from src.modules.hr.models import Employee, LeaveRequest, PerformanceReview
from src.modules.hr.schemas import EmployeeCreate, LeaveRequestCreate, PerformanceReviewCreate


class HRService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_employee(self, org_id: UUID, data: EmployeeCreate) -> Employee:
        emp = Employee(organization_id=org_id, **data.model_dump())
        self.db.add(emp)
        await self.db.flush()
        await self.db.refresh(emp)
        return emp

    async def list_employees(self, org_id: UUID, department: str | None = None, status: str | None = None) -> list[Employee]:
        q = select(Employee).where(Employee.organization_id == org_id)
        if department:
            q = q.where(Employee.department == department)
        if status:
            q = q.where(Employee.status == status)
        q = q.order_by(Employee.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def get_employee(self, employee_id: UUID, org_id: UUID) -> Employee:
        res = await self.db.execute(select(Employee).where(Employee.id == employee_id, Employee.organization_id == org_id))
        emp = res.scalar_one_or_none()
        if not emp:
            raise NotFoundError("Employee")
        return emp

    async def update_employee(self, employee_id: UUID, org_id: UUID, updates: dict) -> Employee:
        emp = await self.get_employee(employee_id, org_id)
        for k, v in updates.items():
            if v is not None:
                setattr(emp, k, v)
        await self.db.flush()
        await self.db.refresh(emp)
        return emp

    async def request_leave(self, org_id: UUID, data: LeaveRequestCreate) -> LeaveRequest:
        await self.get_employee(data.employee_id, org_id)
        req = LeaveRequest(organization_id=org_id, **data.model_dump())
        self.db.add(req)
        await self.db.flush()
        await self.db.refresh(req)
        return req

    async def list_leave_requests(self, org_id: UUID, status: str | None = None) -> list[LeaveRequest]:
        q = select(LeaveRequest).where(LeaveRequest.organization_id == org_id)
        if status:
            q = q.where(LeaveRequest.status == status)
        q = q.order_by(LeaveRequest.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def approve_leave(self, request_id: UUID, org_id: UUID, approved_by_id: UUID) -> LeaveRequest:
        res = await self.db.execute(select(LeaveRequest).where(LeaveRequest.id == request_id, LeaveRequest.organization_id == org_id))
        req = res.scalar_one_or_none()
        if not req:
            raise NotFoundError("LeaveRequest")
        req.status = "approved"
        req.approved_by = approved_by_id
        await self.db.flush()
        await self.db.refresh(req)
        return req

    async def reject_leave(self, request_id: UUID, org_id: UUID) -> LeaveRequest:
        res = await self.db.execute(select(LeaveRequest).where(LeaveRequest.id == request_id, LeaveRequest.organization_id == org_id))
        req = res.scalar_one_or_none()
        if not req:
            raise NotFoundError("LeaveRequest")
        req.status = "rejected"
        await self.db.flush()
        await self.db.refresh(req)
        return req

    async def create_review(self, org_id: UUID, data: PerformanceReviewCreate) -> PerformanceReview:
        await self.get_employee(data.employee_id, org_id)
        review = PerformanceReview(organization_id=org_id, **data.model_dump())
        self.db.add(review)
        await self.db.flush()
        await self.db.refresh(review)
        return review

    async def list_reviews(self, org_id: UUID, employee_id: UUID | None = None) -> list[PerformanceReview]:
        q = select(PerformanceReview).where(PerformanceReview.organization_id == org_id)
        if employee_id:
            q = q.where(PerformanceReview.employee_id == employee_id)
        q = q.order_by(PerformanceReview.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def get_headcount_stats(self, org_id: UUID) -> dict:
        q_total = select(func.count()).select_from(Employee).where(Employee.organization_id == org_id)
        q_active = select(func.count()).select_from(Employee).where(Employee.organization_id == org_id, Employee.status == "active")
        q_leave = select(func.count()).select_from(Employee).where(Employee.organization_id == org_id, Employee.status == "on_leave")

        total = (await self.db.execute(q_total)).scalar_one()
        active = (await self.db.execute(q_active)).scalar_one()
        on_leave = (await self.db.execute(q_leave)).scalar_one()

        return {
            "total": total,
            "active": active,
            "on_leave": on_leave,
            "terminated": total - active - on_leave,
        }