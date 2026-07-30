"""
Axorks OS — Finance API Router
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import paginated_response, success_response
from src.core.tenant import TenantContext
from src.modules.finance.schemas import (
    ExpenseCreate, ExpenseRead,
    InvoiceCreate, InvoiceRead, InvoiceUpdate,
    PaymentRecordRequest, PaymentRead,
)
from src.modules.finance.service import FinanceService

router = APIRouter(prefix="/api/v1/finance", tags=["Finance & Invoicing"])


# ── Invoices ─────────────────────────────────────────────

@router.post("/invoices")
async def create_invoice(data: InvoiceCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = FinanceService(db)
    inv = await svc.create_invoice(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=InvoiceRead.model_validate(inv).model_dump(mode="json"))


@router.get("/invoices")
async def list_invoices(page: int = Query(1, ge=1), per_page: int = Query(25), status: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = FinanceService(db)
    items, total = await svc.list_invoices(ctx.org_id, page, per_page, status)
    return paginated_response([InvoiceRead.model_validate(i).model_dump(mode="json") for i in items], page, per_page, total)


@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = FinanceService(db)
    inv = await svc.get_invoice(invoice_id, ctx.org_id)
    return success_response(data=InvoiceRead.model_validate(inv).model_dump(mode="json"))


@router.patch("/invoices/{invoice_id}")
async def update_invoice(invoice_id: UUID, data: InvoiceUpdate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = FinanceService(db)
    inv = await svc.update_invoice(invoice_id, ctx.org_id, data)
    return success_response(data=InvoiceRead.model_validate(inv).model_dump(mode="json"))


@router.post("/payments")
async def record_payment(data: PaymentRecordRequest, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = FinanceService(db)
    pay = await svc.record_payment(ctx.org_id, data)
    return success_response(data=PaymentRead.model_validate(pay).model_dump(mode="json"))


# ── Expenses ─────────────────────────────────────────────

@router.post("/expenses")
async def create_expense(data: ExpenseCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = FinanceService(db)
    exp = await svc.create_expense(ctx.org_id, ctx.workspace_id, ctx.user_id, data)
    return success_response(data=ExpenseRead.model_validate(exp).model_dump(mode="json"))


@router.get("/expenses")
async def list_expenses(page: int = Query(1, ge=1), per_page: int = Query(25), ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = FinanceService(db)
    items, total = await svc.list_expenses(ctx.org_id, page, per_page)
    return paginated_response([ExpenseRead.model_validate(i).model_dump(mode="json") for i in items], page, per_page, total)


# ── Dashboard & Cash Flow Forecast ────────────────────────

@router.get("/dashboard")
async def get_dashboard_summary(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = FinanceService(db)
    summary = await svc.get_dashboard_summary(ctx.org_id)
    return success_response(data=summary)


@router.get("/forecast")
async def get_cashflow_forecast(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = FinanceService(db)
    forecast = await svc.get_cashflow_forecast(ctx.org_id)
    return success_response(data=forecast)
