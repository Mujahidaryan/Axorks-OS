"""
Axorks OS — Finance Schemas
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class InvoiceItemSchema(BaseModel):
    id: UUID | None = None
    description: str
    quantity: Decimal = Decimal("1.0")
    unit_price: Decimal
    amount: Decimal
    sort_order: int = 0


class InvoiceCreate(BaseModel):
    company_id: UUID | None = None
    project_id: UUID | None = None
    proposal_id: UUID | None = None
    invoice_number: str | None = None
    issue_date: date | None = None
    due_date: date | None = None
    currency: str = "USD"
    notes: str | None = None
    items: list[InvoiceItemSchema] = []


class InvoiceUpdate(BaseModel):
    company_id: UUID | None = None
    project_id: UUID | None = None
    status: str | None = None
    issue_date: date | None = None
    due_date: date | None = None
    currency: str | None = None
    notes: str | None = None
    items: list[InvoiceItemSchema] | None = None


class InvoiceRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    company_id: UUID | None = None
    project_id: UUID | None = None
    proposal_id: UUID | None = None
    invoice_number: str
    status: str
    issue_date: date | None = None
    due_date: date | None = None
    subtotal: Decimal | None = None
    tax_amount: Decimal | None = None
    total: Decimal | None = None
    currency: str
    notes: str | None = None
    pdf_url: str | None = None
    paid_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    project_id: UUID | None = None
    category: str | None = "General"
    description: str | None = None
    amount: Decimal
    currency: str = "USD"
    expense_date: date
    receipt_url: str | None = None


class ExpenseRead(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID
    project_id: UUID | None = None
    category: str | None = None
    description: str | None = None
    amount: Decimal
    currency: str
    expense_date: date
    receipt_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentRecordRequest(BaseModel):
    invoice_id: UUID
    amount: Decimal
    payment_method: str = "stripe"
    transaction_id: str | None = None


class PaymentRead(BaseModel):
    id: UUID
    organization_id: UUID
    invoice_id: UUID
    amount: Decimal
    payment_method: str
    transaction_id: str | None = None
    paid_at: datetime

    model_config = {"from_attributes": True}


class FinanceDashboardSummary(BaseModel):
    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    total_outstanding_invoices: Decimal
    currency: str = "USD"
