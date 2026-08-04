"""
Axorks OS — FastAPI Application Entry Point

Assembles all routers, middleware, exception handlers, and lifecycle hooks.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import get_settings
from src.core.exceptions import register_exception_handlers
from src.core.middleware import register_middleware
from src.modules.ai.router import router as ai_router
from src.modules.analytics.router import router as analytics_router
from src.modules.auth.router import router as auth_router
from src.modules.automation.router import router as automation_router
from src.modules.companies.router import router as companies_router
from src.modules.contacts.router import router as contacts_router
from src.modules.crm.router import router as crm_router
from src.modules.deals.router import router as deals_router
from src.modules.dev.router import router as dev_router
from src.modules.finance.router import router as finance_router
from src.modules.hr.router import router as hr_router
from src.modules.iam.router import router as iam_router
from src.modules.integrations.router import router as integrations_router
from src.modules.knowledge.router import router as knowledge_router
from src.modules.leads.router import router as leads_router
from src.modules.marketing.router import router as marketing_router
from src.modules.organizations.router import router as orgs_router
from src.modules.portal.router import router as portal_router
from src.modules.projects.router import router as projects_router
from src.modules.proposals.router import router as proposals_router
from src.modules.recruitment.router import router as recruitment_router
from src.modules.settings.router import router as settings_router
from src.modules.users.router import router as users_router
from src.modules.workspaces.router import router as workspaces_router
from src.shared.notifications.router import router as notifications_router
from src.shared.notifications.websocket import router as ws_router
from src.shared.search.router import router as search_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    if settings.sentry_dsn:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.app_env,
            traces_sample_rate=0.1 if settings.is_production else 1.0,
        )
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-Powered Operating System for Software Agencies & Consultancies",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

register_middleware(app)
register_exception_handlers(app)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


# Phase 1 routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(orgs_router)
app.include_router(workspaces_router)
app.include_router(settings_router)
app.include_router(notifications_router)
app.include_router(search_router)
app.include_router(ws_router)

# Phase 2 routers
app.include_router(leads_router)

# Phase 3 routers
app.include_router(companies_router)
app.include_router(contacts_router)
app.include_router(deals_router)
app.include_router(crm_router)

# Phase 4 routers
app.include_router(ai_router)

# Phase 5 routers
app.include_router(proposals_router)

# Phase 6 routers
app.include_router(projects_router)

# Phase 7 routers
app.include_router(dev_router)

# Phase 8 routers
app.include_router(portal_router)

# Phase 9 routers
app.include_router(finance_router)

# Phase 10 routers
app.include_router(knowledge_router)

# Phase 11 routers
app.include_router(marketing_router)

# Phase 12 routers
app.include_router(recruitment_router)

# Phase 13 routers
app.include_router(hr_router)

# Phase 14 routers
app.include_router(automation_router)

# Phase 16 routers
app.include_router(analytics_router)

# Phase 17 routers
app.include_router(integrations_router)

# Enterprise IAM & RBAC router
app.include_router(iam_router)
