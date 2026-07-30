import pytest
from uuid import uuid4
from src.modules.analytics.service import AnalyticsService
from src.modules.analytics.schemas import MetricCreate, DashboardCreate

@pytest.mark.asyncio
async def test_analytics_flow(db):
    svc = AnalyticsService(db)
    org_id = uuid4()
    ws_id = uuid4()

    # 1. Create Metric
    m_data = MetricCreate(name="Monthly Recurring Revenue", data={"mrr": 50000, "currency": "USD"})
    metric = await svc.create_metric(org_id, ws_id, m_data)
    assert metric.name == "Monthly Recurring Revenue"

    # 2. Create Dashboard
    d_data = DashboardCreate(title="Executive Overview", layout={"grid": ["mrr_card", "pipeline_chart"]})
    dashboard = await svc.create_dashboard(org_id, ws_id, d_data)
    assert dashboard.title == "Executive Overview"

    # 3. Overview aggregations
    comp_overview = await svc.get_company_overview(org_id)
    assert "leads" in comp_overview
    assert "projects" in comp_overview
