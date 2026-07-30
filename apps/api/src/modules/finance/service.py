"""
Axorks OS — Finance Service
"""

import random
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.modules.finance.models import Expense, Invoice, InvoiceItem, Payment
from src.modules.finance.schemas import ExpenseCreate, InvoiceCreate, InvoiceUpdate, PaymentRecordRequest


class FinanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Invoices ─────────────────────────────────────────────

    async def _generate_invoice_number(self, org_id: UUID) -> str:
        q = select(func.count()).select_from(Invoice).where(Invoice.organization_id == org_id)
        count = (await self.db.execute(q)).scalar_one() + 1
        year = datetime.now().year
        return f"INV-{year}-{count:04d}"

    async def create_invoice(self, org_id: UUID, ws_id: UUID, data: InvoiceCreate) -> Invoice:
        inv_num = data.invoice_number or await self._generate_invoice_number(org_id)

        subtotal = sum((item.amount for item in data.items), Decimal("0.0"))
        tax = subtotal * Decimal("0.0")  # default 0% tax
        total = subtotal + tax

        inv = Invoice(
            organization_id=org_id,
            workspace_id=ws_id,
            company_id=data.company_id,
            project_id=data.project_id,
            proposal_id=data.proposal_id,
            invoice_number=inv_num,
            status="draft",
            issue_date=data.issue_date or date.today(),
            due_date=data.due_date,
            currency=data.currency,
            notes=data.notes,
            subtotal=subtotal,
            tax_amount=tax,
            total=total,
        )
        self.db.add(inv)
        await self.db.flush()

        for item in data.items:
            ii = InvoiceItem(
                invoice_id=inv.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.amount,
                sort_order=item.sort_order,
            )
            self.db.add(ii)

        await self.db.flush()
        await self.db.refresh(inv)
        return inv

    async def get_invoice(self, invoice_id: UUID, org_id: UUID) -> Invoice:
        q = select(Invoice).where(Invoice.id == invoice_id, Invoice.organization_id == org_id, Invoice.deleted_at.is_(None))
        res = await self.db.execute(q)
        inv = res.scalar_one_or_none()
        if not inv:
            raise NotFoundError("Invoice")
        return inv

    async def list_invoices(self, org_id: UUID, page: int = 1, per_page: int = 25, status: str | None = None) -> tuple[list[Invoice], int]:
        q = select(Invoice).where(Invoice.organization_id == org_id, Invoice.deleted_at.is_(None))
        if status:
            q = q.where(Invoice.status == status)
        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        q = q.order_by(Invoice.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        items = list((await self.db.execute(q)).scalars().all())
        return items, total

    async def update_invoice(self, invoice_id: UUID, org_id: UUID, data: InvoiceUpdate) -> Invoice:
        inv = await self.get_invoice(invoice_id, org_id)
        for k, v in data.model_dump(exclude_unset=True, exclude={"items"}).items():
            if v is not None:
                setattr(inv, k, v)

        if data.items is not None:
            subtotal = sum((item.amount for item in data.items), Decimal("0.0"))
            inv.subtotal = subtotal
            inv.total = subtotal

        await self.db.flush()
        await self.db.refresh(inv)
        return inv

    async def record_payment(self, org_id: UUID, data: PaymentRecordRequest) -> Payment:
        inv = await self.get_invoice(data.invoice_id, org_id)
        pay = Payment(
            organization_id=org_id,
            invoice_id=data.invoice_id,
            amount=data.amount,
            payment_method=data.payment_method,
            transaction_id=data.transaction_id or f"txn_{random.randint(100000, 999999)}",
        )
        self.db.add(pay)

        inv.status = "paid"
        inv.paid_at = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(pay)
        return pay

    # ── Expenses ─────────────────────────────────────────────

    async def create_expense(self, org_id: UUID, ws_id: UUID, user_id: UUID, data: ExpenseCreate) -> Expense:
        exp = Expense(organization_id=org_id, workspace_id=ws_id, created_by=user_id, **data.model_dump())
        self.db.add(exp)
        await self.db.flush()
        await self.db.refresh(exp)
        return exp

    async def list_expenses(self, org_id: UUID, page: int = 1, per_page: int = 25) -> tuple[list[Expense], int]:
        q = select(Expense).where(Expense.organization_id == org_id)
        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        q = q.order_by(Expense.expense_date.desc()).offset((page - 1) * per_page).limit(per_page)
        items = list((await self.db.execute(q)).scalars().all())
        return items, total

    # ── Dashboard & Cash Flow Forecast ────────────────────────

    async def get_dashboard_summary(self, org_id: UUID) -> dict:
        rev_q = select(func.coalesce(func.sum(Payment.amount), Decimal("0.0"))).where(Payment.organization_id == org_id)
        total_rev = (await self.db.execute(rev_q)).scalar_one()

        exp_q = select(func.coalesce(func.sum(Expense.amount), Decimal("0.0"))).where(Expense.organization_id == org_id)
        total_exp = (await self.db.execute(exp_q)).scalar_one()

        out_q = select(func.coalesce(func.sum(Invoice.total), Decimal("0.0"))).where(Invoice.organization_id == org_id, Invoice.status != "paid", Invoice.deleted_at.is_(None))
        total_out = (await self.db.execute(out_q)).scalar_one()

        return {
            "total_revenue": float(total_rev),
            "total_expenses": float(total_exp),
            "net_profit": float(total_rev - total_exp),
            "total_outstanding_invoices": float(total_out),
            "currency": "USD",
        }

    async def get_cashflow_forecast(self, org_id: UUID) -> dict:
        summary = await self.get_dashboard_summary(org_id)
        projected_rev = summary["total_revenue"] + summary["total_outstanding_invoices"] + 50000.0
        projected_exp = summary["total_expenses"] + 15000.0
        return {
            "30_day_forecast": {
                "projected_revenue": projected_rev,
                "projected_expenses": projected_exp,
                "projected_cash_flow": projected_rev - projected_exp,
            },
            "confidence_score": 0.88,
        }
