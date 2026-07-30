"""Axorks OS — Analytics Service"""
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import NotFoundError
from src.modules.analytics.models import Metric, Dashboard
from src.modules.analytics.schemas import MetricCreate, DashboardCreate

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Metric CRUD
    async def create_metric(self, org_id: UUID, ws_id: UUID, data: MetricCreate) -> Metric:
        metric = Metric(
            organization_id=org_id,
            workspace_id=ws_id,
            name=data.name,
            data=data.data,
        )
        self.db.add(metric)
        await self.db.flush()
        await self.db.refresh(metric)
        return metric

    async def get_metric(self, metric_id: UUID, org_id: UUID) -> Metric:
        res = await self.db.execute(
            select(Metric).where(
                Metric.id == metric_id,
                Metric.organization_id == org_id,
                Metric.deleted_at.is_(None),
            )
        )
        metric = res.scalar_one_or_none()
        if not metric:
            raise NotFoundError("Metric")
        return metric

    async def list_metrics(self, org_id: UUID) -> list[Metric]:
        q = select(Metric).where(Metric.organization_id == org_id, Metric.deleted_at.is_(None)).order_by(Metric.created_at.desc())
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def update_metric(self, metric_id: UUID, org_id: UUID, updates: dict) -> Metric:
        metric = await self.get_metric(metric_id, org_id)
        for k, v in updates.items():
            if v is not None:
                setattr(metric, k, v)
        await self.db.flush()
        await self.db.refresh(metric)
        return metric

    async def delete_metric(self, metric_id: UUID, org_id: UUID) -> None:
        metric = await self.get_metric(metric_id, org_id)
        metric.deleted_at = func.now()
        await self.db.flush()

    # Dashboard CRUD
    async def create_dashboard(self, org_id: UUID, ws_id: UUID, data: DashboardCreate) -> Dashboard:
        dash = Dashboard(
            organization_id=org_id,
            workspace_id=ws_id,
            title=data.title,
            layout=data.layout,
        )
        self.db.add(dash)
        await self.db.flush()
        await self.db.refresh(dash)
        return dash

    async def get_dashboard(self, dash_id: UUID, org_id: UUID) -> Dashboard:
        res = await self.db.execute(
            select(Dashboard).where(
                Dashboard.id == dash_id,
                Dashboard.organization_id == org_id,
                Dashboard.deleted_at.is_(None),
            )
        )
        dash = res.scalar_one_or_none()
        if not dash:
            raise NotFoundError("Dashboard")
        return dash

    async def list_dashboards(self, org_id: UUID) -> list[Dashboard]:
        q = select(Dashboard).where(Dashboard.organization_id == org_id, Dashboard.deleted_at.is_(None)).order_by(Dashboard.created_at.desc())
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def update_dashboard(self, dash_id: UUID, org_id: UUID, updates: dict) -> Dashboard:
        dash = await self.get_dashboard(dash_id, org_id)
        for k, v in updates.items():
            if v is not None:
                setattr(dash, k, v)
        await self.db.flush()
        await self.db.refresh(dash)
        return dash

    async def delete_dashboard(self, dash_id: UUID, org_id: UUID) -> None:
        dash = await self.get_dashboard(dash_id, org_id)
        dash.deleted_at = func.now()
        await self.db.flush()

    # ── Aggregation Dashboards ─────────────────────────────────

    async def get_company_overview(self, org_id: UUID) -> dict:
        """High-level company KPIs across all domains."""
        from src.modules.leads.models import Lead
        from src.modules.companies.models import Company
        from src.modules.projects.models import Project
        from src.modules.finance.models import Invoice

        lead_count = (await self.db.execute(
            select(func.count()).select_from(Lead).where(Lead.organization_id == org_id, Lead.deleted_at.is_(None))
        )).scalar_one()
        company_count = (await self.db.execute(
            select(func.count()).select_from(Company).where(Company.organization_id == org_id, Company.deleted_at.is_(None))
        )).scalar_one()
        project_count = (await self.db.execute(
            select(func.count()).select_from(Project).where(Project.organization_id == org_id, Project.deleted_at.is_(None))
        )).scalar_one()
        invoice_count = (await self.db.execute(
            select(func.count()).select_from(Invoice).where(Invoice.organization_id == org_id, Invoice.deleted_at.is_(None))
        )).scalar_one()

        return {
            "leads": lead_count,
            "companies": company_count,
            "projects": project_count,
            "invoices": invoice_count,
        }

    async def get_sales_overview(self, org_id: UUID) -> dict:
        """Sales pipeline metrics."""
        from src.modules.leads.models import Lead
        from src.modules.deals.models import Deal

        stages = ["new", "contacted", "qualified", "proposal", "negotiation", "won", "lost"]
        by_stage: dict[str, int] = {}
        for stage in stages:
            count = (await self.db.execute(
                select(func.count()).select_from(Lead).where(
                    Lead.organization_id == org_id, Lead.status == stage, Lead.deleted_at.is_(None)
                )
            )).scalar_one()
            by_stage[stage] = count

        won_deals_value = (await self.db.execute(
            select(func.coalesce(func.sum(Deal.value), 0)).where(
                Deal.organization_id == org_id, Deal.stage == "won", Deal.deleted_at.is_(None)
            )
        )).scalar_one()

        return {"leads_by_stage": by_stage, "won_deals_value": float(won_deals_value)}

    async def get_finance_overview(self, org_id: UUID) -> dict:
        """Finance summary metrics."""
        from src.modules.finance.models import Invoice, Expense

        total_revenue = (await self.db.execute(
            select(func.coalesce(func.sum(Invoice.total), 0)).where(
                Invoice.organization_id == org_id, Invoice.status == "paid", Invoice.deleted_at.is_(None)
            )
        )).scalar_one()
        total_outstanding = (await self.db.execute(
            select(func.coalesce(func.sum(Invoice.total), 0)).where(
                Invoice.organization_id == org_id, Invoice.status.in_(["sent", "overdue"]), Invoice.deleted_at.is_(None)
            )
        )).scalar_one()
        total_expenses = (await self.db.execute(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.organization_id == org_id, Expense.deleted_at.is_(None)
            )
        )).scalar_one()

        return {
            "total_revenue": float(total_revenue),
            "total_outstanding": float(total_outstanding),
            "total_expenses": float(total_expenses),
            "net_profit": float(total_revenue) - float(total_expenses),
        }

    async def get_projects_overview(self, org_id: UUID) -> dict:
        """Project metrics."""
        from src.modules.projects.models import Project, Task

        status_counts: dict[str, int] = {}
        for status in ["planning", "active", "on_hold", "completed", "cancelled"]:
            count = (await self.db.execute(
                select(func.count()).select_from(Project).where(
                    Project.organization_id == org_id, Project.status == status, Project.deleted_at.is_(None)
                )
            )).scalar_one()
            status_counts[status] = count

        total_tasks = (await self.db.execute(
            select(func.count()).select_from(Task).where(
                Task.organization_id == org_id, Task.deleted_at.is_(None)
            )
        )).scalar_one()

        return {"projects_by_status": status_counts, "total_tasks": total_tasks}
