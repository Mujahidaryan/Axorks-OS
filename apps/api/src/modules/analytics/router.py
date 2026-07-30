"""Axorks OS — Analytics Router"""
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.analytics.schemas import MetricCreate, MetricRead, DashboardCreate, DashboardRead
from src.modules.analytics.service import AnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

# Metric endpoints
@router.post("/metrics")
async def create_metric(data: MetricCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    metric = await svc.create_metric(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=MetricRead.model_validate(metric).model_dump(mode="json"))

@router.get("/metrics")
async def list_metrics(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    metrics = await svc.list_metrics(ctx.org_id)
    return success_response(data=[MetricRead.model_validate(m).model_dump(mode="json") for m in metrics])

@router.get("/metrics/{metric_id}")
async def get_metric(metric_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    metric = await svc.get_metric(metric_id, ctx.org_id)
    return success_response(data=MetricRead.model_validate(metric).model_dump(mode="json"))

@router.patch("/metrics/{metric_id}")
async def update_metric(metric_id: UUID, updates: dict, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    metric = await svc.update_metric(metric_id, ctx.org_id, updates)
    return success_response(data=MetricRead.model_validate(metric).model_dump(mode="json"))

@router.delete("/metrics/{metric_id}")
async def delete_metric(metric_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    await svc.delete_metric(metric_id, ctx.org_id)
    return success_response(data={"deleted": True})

# Dashboard endpoints
@router.post("/dashboards")
async def create_dashboard(data: DashboardCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    dash = await svc.create_dashboard(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=DashboardRead.model_validate(dash).model_dump(mode="json"))

@router.get("/dashboards")
async def list_dashboards(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    dashboards = await svc.list_dashboards(ctx.org_id)
    return success_response(data=[DashboardRead.model_validate(d).model_dump(mode="json") for d in dashboards])

@router.get("/dashboards/{dash_id}")
async def get_dashboard(dash_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    dash = await svc.get_dashboard(dash_id, ctx.org_id)
    return success_response(data=DashboardRead.model_validate(dash).model_dump(mode="json"))

@router.patch("/dashboards/{dash_id}")
async def update_dashboard(dash_id: UUID, updates: dict, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    dash = await svc.update_dashboard(dash_id, ctx.org_id, updates)
    return success_response(data=DashboardRead.model_validate(dash).model_dump(mode="json"))

@router.delete("/dashboards/{dash_id}")
async def delete_dashboard(dash_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AnalyticsService(db)
    await svc.delete_dashboard(dash_id, ctx.org_id)
    return success_response(data={"deleted": True})


# ── Aggregation Dashboards ────────────────────────────────────


@router.get("/overview/company")
async def company_overview(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    """High-level company KPIs across all domains."""
    svc = AnalyticsService(db)
    data = await svc.get_company_overview(ctx.org_id)
    return success_response(data=data)


@router.get("/overview/sales")
async def sales_overview(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    """Sales pipeline metrics."""
    svc = AnalyticsService(db)
    data = await svc.get_sales_overview(ctx.org_id)
    return success_response(data=data)


@router.get("/overview/finance")
async def finance_overview(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    """Finance summary metrics."""
    svc = AnalyticsService(db)
    data = await svc.get_finance_overview(ctx.org_id)
    return success_response(data=data)


@router.get("/overview/projects")
async def projects_overview(ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    """Project metrics."""
    svc = AnalyticsService(db)
    data = await svc.get_projects_overview(ctx.org_id)
    return success_response(data=data)
