"""
Axorks OS — Phase 9: Finance Tests

Tests invoice CRUD with line items, payment recording, expense tracking, dashboard summary, and cash flow forecast.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_finance_flow(auth_client: AsyncClient):
    # 1. Create Invoice with line items
    res = await auth_client.post(
        "/api/v1/finance/invoices",
        json={
            "notes": "Monthly retainer - July 2026",
            "items": [
                {"description": "UI/UX Design Sprint", "quantity": 1, "unit_price": 8000, "amount": 8000, "sort_order": 0},
                {"description": "Full-Stack Development", "quantity": 2, "unit_price": 12000, "amount": 24000, "sort_order": 1},
            ],
        },
    )
    assert res.status_code == 200
    inv = res.json()["data"]
    inv_id = inv["id"]
    assert inv["status"] == "draft"
    assert float(inv["total"]) == 32000.0

    # 2. List Invoices
    res = await auth_client.get("/api/v1/finance/invoices")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 3. Get Single Invoice
    res = await auth_client.get(f"/api/v1/finance/invoices/{inv_id}")
    assert res.status_code == 200
    assert res.json()["data"]["invoice_number"].startswith("INV-")

    # 4. Update Invoice Status
    res = await auth_client.patch(f"/api/v1/finance/invoices/{inv_id}", json={"status": "sent"})
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "sent"

    # 5. Record Payment
    res = await auth_client.post(
        "/api/v1/finance/payments",
        json={"invoice_id": inv_id, "amount": 32000, "payment_method": "bank_transfer"},
    )
    assert res.status_code == 200
    assert float(res.json()["data"]["amount"]) == 32000.0

    # 6. Verify Invoice is now Paid
    res = await auth_client.get(f"/api/v1/finance/invoices/{inv_id}")
    assert res.json()["data"]["status"] == "paid"

    # 7. Create Expense
    res = await auth_client.post(
        "/api/v1/finance/expenses",
        json={"category": "Infrastructure", "description": "AWS monthly bill", "amount": 4500, "expense_date": "2026-07-15"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["category"] == "Infrastructure"

    # 8. List Expenses
    res = await auth_client.get("/api/v1/finance/expenses")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 9. Dashboard Summary
    res = await auth_client.get("/api/v1/finance/dashboard")
    assert res.status_code == 200
    summary = res.json()["data"]
    assert summary["total_revenue"] >= 32000.0
    assert summary["total_expenses"] >= 4500.0

    # 10. Cash Flow Forecast
    res = await auth_client.get("/api/v1/finance/forecast")
    assert res.status_code == 200
    assert "30_day_forecast" in res.json()["data"]
    assert res.json()["data"]["confidence_score"] > 0
