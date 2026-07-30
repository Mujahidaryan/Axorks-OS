import pytest
from datetime import date
from uuid import uuid4
from src.modules.hr.service import HRService
from src.modules.hr.schemas import EmployeeCreate, LeaveRequestCreate, PerformanceReviewCreate

@pytest.mark.asyncio
async def test_hr_flow(db):
    svc = HRService(db)
    org_id = uuid4()
    approver_id = uuid4()

    # 1. Create Employee
    emp_data = EmployeeCreate(full_name="John Smith", email="john@example.com", department="Product", job_title="PM")
    emp = await svc.create_employee(org_id, emp_data)
    assert emp.full_name == "John Smith"

    # 2. Leave Request
    lr_data = LeaveRequestCreate(employee_id=emp.id, leave_type="annual", start_date=date(2026, 8, 1), end_date=date(2026, 8, 5), days_count=5)
    leave = await svc.request_leave(org_id, lr_data)
    assert leave.status == "pending"

    # 3. Approve Leave
    approved = await svc.approve_leave(leave.id, org_id, approver_id)
    assert approved.status == "approved"

    # 4. Performance Review
    rev_data = PerformanceReviewCreate(employee_id=emp.id, overall_rating=5, strengths="Great leadership")
    review = await svc.create_review(org_id, rev_data)
    assert review.overall_rating == 5

    # 5. Headcount Stats
    stats = await svc.get_headcount_stats(org_id)
    assert stats["total"] == 1
    assert stats["active"] == 1
