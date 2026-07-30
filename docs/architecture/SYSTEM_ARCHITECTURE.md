# Axorks OS — System Architecture

> Version 1.0 | Principal Architecture Document

---

## 1. Executive Summary

Axorks OS is a **multi-tenant SaaS operating system** designed from day one for software agencies and consulting firms. It unifies sales, delivery, finance, HR, marketing, and client collaboration into one AI-native product.

This document defines the complete system architecture: layers, services, data flow, deployment topology, and engineering principles.

---

## 2. Architecture Principles

| Principle | Rule |
|-----------|------|
| **One Product Feel** | No app-switching UX. Shared shell, command palette, search, and design system everywhere |
| **Multi-Tenant First** | Organization → Workspace → Resource isolation from day one |
| **AI as Infrastructure** | AI is not a feature page — it is a cross-cutting layer on every screen |
| **Minimal Cognitive Load** | One screen, one task, one purpose. Optional fields by default |
| **Scale by Design** | PostgreSQL partitioning, indexes, caching, event sourcing where warranted |
| **Never Overengineer** | Clean Architecture where beneficial; YAGNI everywhere else |
| **Provider Abstraction** | AI, email, storage, payments — all behind interfaces |
| **Audit Everything** | Activity logs, audit trails, version history on critical entities |

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENTS                                       │
│   Web Browser (Desktop)  │  PWA / Mobile  │  Client Portal  │  API     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTPS
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     CDN / EDGE (Cloudflare)                             │
│              Static Assets │ WAF │ Rate Limiting │ DDoS                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
          ┌──────────────────────┴──────────────────────┐
          ▼                                              ▼
┌─────────────────────┐                    ┌─────────────────────────────┐
│   FRONTEND (Vercel) │                    │   BACKEND API (Railway)     │
│   Next.js 15 App    │◄──── REST/GraphQL ─►│   FastAPI                   │
│   React + TS        │      WebSocket       │   Python 3.12+              │
│   shadcn/ui         │                      │   SQLAlchemy 2.0            │
│   TanStack Query    │                      │   Pydantic v2               │
└─────────────────────┘                    └───────────┬─────────────────┘
                                                       │
         ┌─────────────┬─────────────┬───────────────┼───────────────┐
         ▼             ▼             ▼               ▼               ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
   │ Neon     │  │ Upstash  │  │ Cloudinary│  │ Resend   │  │ AI Providers │
   │ Postgres │  │ Redis    │  │ / R2      │  │ Email    │  │ OpenAI etc.  │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────────┘
         │
         ▼
   ┌──────────────────────────────────────────────────────────────────────┐
   │                    BACKGROUND WORKERS (Railway / Celery)             │
   │   Email │ AI Jobs │ CSV Import │ Webhooks │ Automation │ Reports    │
   └──────────────────────────────────────────────────────────────────────┘
         │
         ▼
   ┌──────────────────────────────────────────────────────────────────────┐
   │                    OBSERVABILITY                                       │
   │   Sentry │ PostHog │ Axiom / Better Stack │ OpenTelemetry (future)  │
   └──────────────────────────────────────────────────────────────────────┘
```

---

## 4. Backend Decision: FastAPI over NestJS

**Recommendation: FastAPI**

| Factor | FastAPI | NestJS |
|--------|---------|--------|
| AI ecosystem | Native Python — LangChain, transformers, CV parsers | Requires Python microservices for AI-heavy work |
| Performance | Comparable for I/O-bound SaaS | Comparable |
| Typing | Pydantic v2 — excellent | TypeScript — excellent |
| OpenAPI | Auto-generated, first-class | Supported via Swagger |
| Background jobs | Celery, ARQ, native async | BullMQ |
| Team strength | Python (Axorks) | TypeScript |
| ORM | SQLAlchemy 2.0 + Alembic | Prisma |

**Verdict:** FastAPI for API + AI workloads. Next.js frontend shares types via OpenAPI-generated TypeScript client in `packages/types`.

---

## 5. Application Layers (Backend)

```
apps/api/
├── src/
│   ├── main.py                    # FastAPI app entry
│   ├── core/                      # Config, security, dependencies
│   │   ├── config.py
│   │   ├── security.py            # JWT, OAuth, 2FA
│   │   ├── database.py            # Session factory
│   │   ├── cache.py               # Redis client
│   │   └── tenant.py              # Multi-tenant context middleware
│   ├── modules/                   # Feature-based modules
│   │   ├── auth/
│   │   ├── organizations/
│   │   ├── workspaces/
│   │   ├── leads/
│   │   ├── crm/
│   │   ├── proposals/
│   │   ├── projects/
│   │   ├── finance/
│   │   ├── hr/
│   │   ├── knowledge/
│   │   ├── marketing/
│   │   ├── automation/
│   │   ├── integrations/
│   │   ├── ai/
│   │   └── analytics/
│   ├── shared/                    # Cross-cutting
│   │   ├── events/                # Domain events
│   │   ├── audit/                 # Audit log service
│   │   ├── search/                # Full-text search
│   │   ├── notifications/
│   │   └── storage/
│   └── workers/                   # Celery tasks
├── alembic/                       # Migrations
└── tests/
```

### Layer Responsibilities

| Layer | Responsibility |
|-------|----------------|
| **Router** | HTTP validation, auth guards, response serialization |
| **Service** | Business logic, orchestration, permissions |
| **Repository** | Database queries, tenant scoping |
| **Model** | SQLAlchemy ORM entities |
| **Schema** | Pydantic request/response DTOs |
| **Event** | Domain events for automation and audit |

---

## 6. Frontend Architecture

```
apps/web/
├── app/                           # Next.js App Router
│   ├── (auth)/                    # Login, register, 2FA
│   ├── (app)/                     # Authenticated shell
│   │   ├── layout.tsx             # Global shell: sidebar, cmd+k, search
│   │   ├── leads/
│   │   ├── crm/[id]/              # One-page CRM
│   │   ├── projects/
│   │   ├── finance/
│   │   └── ...
│   └── (portal)/                  # Client portal (separate layout)
├── components/
│   ├── ui/                        # shadcn primitives
│   ├── shell/                     # App chrome
│   ├── ai/                        # AI inline components
│   └── features/                  # Feature-specific components
├── hooks/
├── lib/
│   ├── api-client.ts              # Generated from OpenAPI
│   └── ai-context.tsx
├── stores/                        # Zustand for UI state only
└── styles/
```

### Frontend State Strategy

| State Type | Tool |
|------------|------|
| Server data | TanStack Query |
| Forms | React Hook Form + Zod |
| UI ephemeral | Zustand or React state |
| URL state | nuqs / searchParams |
| Real-time | WebSocket + TanStack Query invalidation |

---

## 7. Multi-Tenancy Model

```
Organization (tenant root)
├── billing, plan, settings
├── Members (users with org-level roles)
└── Workspaces (logical divisions: Sales, Delivery, Internal)
    ├── Workspace Members (workspace-scoped roles)
    └── All business data (leads, projects, invoices...)
        └── Scoped by organization_id + workspace_id
```

### Data Isolation Rules

1. **Every table** has `organization_id` (required, indexed).
2. **Workspace-scoped tables** also have `workspace_id`.
3. **Row-Level Security** enforced at repository layer — never trust client filters.
4. **Middleware** extracts tenant context from JWT claims on every request.
5. **Soft deletes** via `deleted_at` — never hard delete business records.
6. **Audit log** captures who changed what, when, from which IP.

### Tenant Context Flow

```
JWT → Auth Middleware → TenantContext(org_id, workspace_id, user_id, roles)
                              ↓
                    Repository Base Class (auto-filters all queries)
                              ↓
                    Service Layer (permission checks)
```

---

## 8. Authentication & Authorization

### Auth Stack

| Component | Implementation |
|-----------|----------------|
| Primary auth | Better Auth (self-hosted) or Clerk (managed) |
| Sessions | JWT access token (15 min) + refresh token (7 days, rotating) |
| OAuth | Google, Microsoft |
| 2FA | TOTP (authenticator app) |
| API keys | For integrations and webhooks (scoped, revocable) |

### RBAC Model

```
Roles (per organization):
  owner → admin → manager → member → viewer → client (portal only)

Permissions (granular, resource + action):
  leads:read, leads:write, leads:delete, leads:assign
  projects:read, projects:write, ...
  finance:read, finance:write, ...
  settings:manage, users:invite, ...

Custom roles (future): Admin defines role → permission mapping
```

### Permission Check Pattern

```python
@require_permission("leads:write")
async def update_lead(lead_id: UUID, data: LeadUpdate, ctx: TenantContext):
    ...
```

---

## 9. API Design

### REST Conventions

```
GET    /api/v1/leads              # List (paginated, filtered, sorted)
POST   /api/v1/leads              # Create
GET    /api/v1/leads/{id}         # Detail
PATCH  /api/v1/leads/{id}         # Partial update
DELETE /api/v1/leads/{id}         # Soft delete

GET    /api/v1/leads/{id}/timeline    # Activity timeline
POST   /api/v1/leads/{id}/notes       # Nested resources
POST   /api/v1/ai/suggest             # AI endpoints
```

### Standard Response Envelope

```json
{
  "data": {},
  "meta": { "page": 1, "per_page": 25, "total": 1042 },
  "errors": null
}
```

### Pagination, Filtering, Sorting

- Cursor-based pagination for timelines and feeds
- Offset pagination for admin tables
- Filter query params: `?status=qualified&owner_id=uuid&tags=enterprise`
- Full-text search via dedicated `/search` endpoint (PostgreSQL tsvector + Redis cache)

---

## 10. Real-Time Architecture

| Use Case | Technology |
|----------|------------|
| Notifications | WebSocket (FastAPI) or SSE |
| Live CRM updates | WebSocket room per entity |
| AI streaming responses | SSE from FastAPI |
| Presence (future) | Redis pub/sub |

---

## 11. Event-Driven Architecture

### Domain Events

```
LeadCreated → [AssignOwner, SendNotification, RunScoring, TriggerAutomation]
ProposalSent → [CreateActivity, ScheduleFollowUp, UpdatePipeline]
InvoicePaid → [UpdateFinance, NotifyTeam, TriggerWebhook]
```

### Event Store (Selective)

Use event sourcing for:
- Automation execution history
- Audit-critical financial transactions
- AI action confirmations

Use simple activity log for:
- CRM timeline
- User-facing history

### Automation Engine (Phase 14)

```
Trigger (event or schedule)
  → Conditions (visual rule builder, JSON logic)
    → Actions (email, assign, create task, webhook, AI generate)
      → Execution log (retry, idempotency key)
```

---

## 12. Search Architecture

```
User Query
    ↓
Command Palette / Global Search
    ↓
Search API → PostgreSQL tsvector (primary)
           → Redis cache (hot queries, 60s TTL)
           → Future: Meilisearch/Typesense at 1M+ records
    ↓
Results grouped by entity type (Leads, Projects, Invoices, Docs...)
```

### Indexed Entities

Leads, Companies, Contacts, Projects, Tasks, Invoices, Documents, Knowledge articles, Employees, Candidates.

---

## 13. File Storage Architecture

| Phase | Provider | Use |
|-------|----------|-----|
| MVP | Cloudinary | Uploads, transforms, CDN |
| Scale | Cloudflare R2 | Cost-effective object storage |

### File Metadata (PostgreSQL)

```
files: id, organization_id, workspace_id, entity_type, entity_id,
       filename, mime_type, size_bytes, storage_key, uploaded_by, created_at
```

---

## 14. Background Job Architecture

| Queue | Jobs |
|-------|------|
| `high` | AI streaming prep, real-time notifications |
| `default` | Email send, webhook delivery |
| `low` | CSV import, report generation, bulk scoring |
| `scheduled` | Cron: follow-up reminders, recurring invoices |

**Implementation:** Celery + Redis (Upstash) or ARQ for lighter MVP.

---

## 15. Integration Architecture

### Integration Pattern

```
OAuth Connect → Store encrypted tokens → Webhook receiver → Normalize → Domain event
```

### Integration Registry

Each integration implements:

```python
class IntegrationProvider(Protocol):
    name: str
    oauth_scopes: list[str]
    connect(user_id) -> AuthResult
    sync(entity_type) -> SyncResult
    handle_webhook(payload) -> list[DomainEvent]
```

### Priority Integrations (Phase 17)

GitHub/GitLab, Google Workspace, Microsoft 365, Slack, Stripe, Resend, LinkedIn (compliant), WhatsApp Business API.

---

## 16. Deployment Topology

| Service | Platform | Environment |
|---------|----------|-------------|
| Frontend | Vercel | Production, Preview (PR), Development |
| API | Railway | Production, Staging |
| Workers | Railway | Same project, separate process |
| PostgreSQL | Neon | Production + branch per PR (optional) |
| Redis | Upstash | Global |
| CDN/WAF | Cloudflare | DNS + proxy |

### CI/CD Pipeline

```
Push → GitHub Actions
  → Lint (Ruff, ESLint) + Type check (mypy, tsc)
  → Unit tests
  → Integration tests (testcontainers PostgreSQL)
  → Build Docker image (API)
  → Deploy preview (Vercel + Railway staging)
  → Manual promote to production
```

### Environment Variables

Managed via platform secrets. Never committed. Rotated quarterly.

---

## 17. Scalability Roadmap

| Scale | Strategy |
|-------|----------|
| 0–100K leads | Single Neon instance, Redis cache, proper indexes |
| 100K–1M leads | Read replicas, connection pooling (PgBouncer), partition leads by org |
| 1M–10M leads | Table partitioning by organization_id, dedicated search engine |
| 10M+ activities | Time-series partitioning on activity_log, archival to cold storage |

### Critical Indexes (Leads Example)

```sql
CREATE INDEX idx_leads_org_workspace ON leads (organization_id, workspace_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_status ON leads (organization_id, status) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_owner ON leads (organization_id, owner_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_search ON leads USING gin(to_tsvector('english', coalesce(business_name,'') || ' ' || coalesce(notes,'')));
```

---

## 18. Observability

| Concern | Tool |
|---------|------|
| Error tracking | Sentry |
| Product analytics | PostHog |
| Structured logging | Axiom or Better Stack |
| Uptime | Better Stack or UptimeRobot |
| API metrics | Railway metrics + custom Prometheus (future) |

### Structured Log Format

```json
{
  "timestamp": "ISO8601",
  "level": "info",
  "service": "api",
  "trace_id": "uuid",
  "organization_id": "uuid",
  "user_id": "uuid",
  "action": "lead.created",
  "duration_ms": 45
}
```

---

## 19. Feature Module Map

| Module | Phase | Core Entities |
|--------|-------|---------------|
| Foundation | 1 | User, Organization, Workspace, Role, Setting, Notification |
| Lead Intelligence | 2 | Lead, LeadSource, LeadScore, LeadTag |
| CRM | 3 | Contact, Company, Deal, Activity, Note, Call, Email |
| AI Sales | 4 | Conversation, AISuggestion, Requirement, Objection |
| Proposals | 5 | Proposal, Quotation, Contract, SOW, Milestone |
| Projects | 6 | Project, Epic, Story, Task, Sprint, TimeEntry |
| Dev Hub | 7 | Repository, PullRequest, Deployment, Environment |
| Client Portal | 8 | PortalUser, Approval, SupportTicket |
| Finance | 9 | Invoice, Expense, Payment, Subscription, TaxRecord |
| Knowledge | 10 | Article, SOP, Template, PromptLibrary |
| Marketing | 11 | Campaign, Funnel, ContentPost, AnalyticsSnapshot |
| Recruitment | 12 | Candidate, Interview, Assessment, Offer |
| HR | 13 | Employee, Attendance, Leave, Payroll, Goal |
| Automation | 14 | Workflow, Trigger, Condition, Action, Execution |
| Analytics | 16 | Dashboard, Widget, Report, Metric |

---

## 20. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Page load (LCP) | < 2.5s |
| API p95 latency | < 300ms (non-AI) |
| AI first token | < 1.5s |
| Uptime | 99.9% |
| Accessibility | WCAG 2.2 AA |
| Data retention | Configurable per org, default 7 years finance |
| Backup | Daily automated, point-in-time recovery (Neon) |
| RPO / RTO | 1 hour / 4 hours |

---

## 21. Coding Standards

- **Python:** Ruff, mypy strict, pytest
- **TypeScript:** ESLint, Prettier, strict mode
- **Commits:** Conventional commits (`feat:`, `fix:`, `docs:`)
- **PRs:** Required review, CI green, no direct main pushes
- **API:** OpenAPI spec is source of truth for frontend client generation
- **Tests:** Unit tests for services, integration tests for critical workflows

---

## 22. Security Summary

See [SECURITY_ARCHITECTURE.md](./SECURITY_ARCHITECTURE.md) for full detail.

- OWASP Top 10 mitigations
- Encryption at rest (Neon) and in transit (TLS 1.3)
- Secrets in platform vaults
- Rate limiting per IP and per org
- CSRF protection on cookie-based flows
- Input validation via Pydantic/Zod on every boundary
- AI actions require explicit user confirmation for destructive operations

---

## 23. Future Commercial SaaS Readiness

Even as single-tenant usage today, the architecture supports:

- Self-serve signup (Phase: add billing module)
- Stripe subscription plans
- Usage-based AI metering
- White-label client portals
- Marketplace for integrations
- SOC 2 preparation (audit logs, access controls already in place)

---

*This document is the canonical reference for all engineering decisions on Axorks OS.*
