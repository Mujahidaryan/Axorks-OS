# Axorks OS — Phase Implementation Prompts

> Use AFTER giving the AI the [Master Prompt](../AXORKS_OS_MASTER_PROMPT.md).
> Give ONE phase prompt at a time. Complete and verify each phase before proceeding.

---

## How to Use

```
Session Start  →  Paste AXORKS_OS_MASTER_PROMPT.md
Implementation →  Paste the specific PHASE below
Verification   →  Test acceptance criteria before next phase
```

---

# PHASE 1 — Foundation

## Prompt

```
Implement Phase 1: Foundation for Axorks OS.

CONTEXT: Read the Master Prompt and System Architecture docs first.

GOAL: Build the core platform shell that every future module depends on.

MONOREPO SETUP:
- Initialize monorepo: apps/web (Next.js 15), apps/api (FastAPI), packages/ui, packages/types, packages/utils
- Docker Compose for local dev (PostgreSQL, Redis)
- GitHub Actions CI (lint, type-check, test)
- Environment variable templates (.env.example)

BACKEND (apps/api — FastAPI):
1. Project scaffold with feature-based module structure
2. PostgreSQL connection via SQLAlchemy 2.0 + Alembic migrations
3. Redis connection for caching and sessions
4. Authentication:
   - Email/password registration and login
   - JWT access token (15 min) + refresh token (7 day, rotating, httpOnly cookie)
   - OAuth 2.0: Google, Microsoft
   - 2FA via TOTP
   - Password reset flow
5. Authorization:
   - RBAC with roles: owner, admin, manager, member, viewer
   - Permission system: resource:action pattern
   - Middleware: extract TenantContext (org_id, workspace_id, user_id, roles) from JWT
6. Organizations:
   - CRUD organizations
   - Auto-create default workspace on org creation
   - Organization settings (JSONB)
7. Workspaces:
   - CRUD workspaces within organization
   - Workspace members with roles
8. User profile:
   - GET/PATCH profile
   - Avatar upload
   - Timezone, locale preferences
9. Settings:
   - Organization settings API
   - Workspace settings API
   - User preferences API
10. Notifications:
    - Create, list, mark read
    - WebSocket or SSE for real-time delivery
11. Audit logs:
    - Auto-log all mutations (create, update, delete) with old/new values
12. Activity logs:
    - User-facing timeline entries
13. Global search:
    - POST /api/v1/search — full-text search across indexed entities
    - PostgreSQL tsvector
14. API standards:
    - REST conventions, pagination, filtering, sorting
    - Standard response envelope: { data, meta, errors }
    - OpenAPI auto-generation

FRONTEND (apps/web — Next.js 15):
1. App shell layout:
   - Collapsible sidebar navigation
   - Top bar with search, notifications bell, profile menu
   - Breadcrumbs
2. Authentication pages:
   - Login, register, forgot password, 2FA verification
   - OAuth callback handling
3. Command palette (Cmd+K / Ctrl+K):
   - Fuzzy search navigation to all routes
   - Quick actions (create lead, new project, etc.)
   - Recent items
4. Global search:
   - Search bar in top nav
   - Results grouped by entity type
5. Dark mode / Light mode:
   - System preference detection
   - Manual toggle in settings
   - Persist preference
6. Settings pages:
   - Organization settings
   - Workspace settings
   - Profile settings
   - Security (2FA setup, sessions, API keys)
   - Keyboard shortcuts reference
   - Preferences (theme, locale, timezone)
7. Notifications panel:
   - Dropdown with unread count
   - Mark as read, mark all read
8. Keyboard shortcuts:
   - Cmd+K: command palette
   - Cmd+/: shortcut help
   - G then L: go to leads (etc.)
9. Shared UI components (packages/ui):
   - shadcn/ui setup with Tailwind
   - Button, Input, Select, Dialog, Dropdown, Table, Badge, Avatar, Tabs, Toast
   - Loading skeletons, empty states, error boundaries

DATABASE MIGRATIONS:
- organizations, workspaces, users, organization_members, workspace_members
- roles, role_assignments
- audit_logs, activity_logs, notifications
- sessions, refresh_tokens

SECURITY:
- Rate limiting on auth endpoints
- CSRF protection
- Secure headers middleware
- Input validation on all endpoints (Pydantic / Zod)

ACCEPTANCE CRITERIA:
- [ ] User can register, login, enable 2FA, logout
- [ ] User can create organization with default workspace
- [ ] RBAC enforced: member cannot access admin settings
- [ ] Cmd+K opens command palette with navigation
- [ ] Global search returns results
- [ ] Dark/light mode toggles and persists
- [ ] Notifications appear in real-time
- [ ] Audit log records all entity mutations
- [ ] All API endpoints documented in OpenAPI
- [ ] CI pipeline passes lint + type-check + tests
```

---

# PHASE 2 — Lead Intelligence

## Prompt

```
Implement Phase 2: Lead Intelligence for Axorks OS.

PREREQUISITE: Phase 1 complete and verified.

GOAL: Build the lead capture, scoring, and management system — the heart of Axorks OS sales.

BACKEND:
1. Lead CRUD API:
   - POST/GET/PATCH/DELETE /api/v1/leads
   - List with pagination, filtering (status, source, owner, tags, score range), sorting
   - All fields optional except organization context
2. Lead fields:
   - business_name, website, industry, country, company_size, revenue_range, linkedin_url
   - decision_maker_name, decision_maker_title, phone, email
   - source (enum: linkedin, instagram, facebook, youtube, website, cold_call, cold_email, referral, manual, csv, api, google_business, directory, other)
   - source_detail, status (enum: new, contacted, qualified, proposal, negotiation, won, lost, archived)
   - score (0-100), owner_id, notes, tags[], custom_fields (JSONB)
3. Lead assignment:
   - PATCH /api/v1/leads/{id}/assign — assign to team member
   - Bulk assign: POST /api/v1/leads/bulk-assign
4. Lead scoring:
   - Manual score update with history (lead_score_history table)
   - AI-assisted scoring endpoint: POST /api/v1/leads/{id}/score (uses AI provider layer)
5. CSV import:
   - POST /api/v1/leads/import — upload CSV, validate, import async via background job
   - Import status tracking (lead_imports table)
   - Column mapping UI support
   - Max 10K rows per import
6. API lead creation:
   - POST /api/v1/leads (API key auth for external integrations)
7. Lead timeline:
   - GET /api/v1/leads/{id}/timeline — activity log for this lead
8. Tags management:
   - Auto-complete existing tags
   - Bulk tag/untag
9. Full-text search:
   - Leads indexed in search_vector (tsvector trigger)
   - Searchable via global search endpoint

FRONTEND:
1. Lead list page (/leads):
   - Table view with sortable columns
   - Board view (kanban by status)
   - Filters: status, source, owner, tags, score, date range
   - Bulk actions: assign, tag, change status, delete
   - Quick search within leads
2. Lead create/edit:
   - Form with ALL fields optional
   - Source selector
   - Tag input with autocomplete
   - Owner assignment dropdown
   - Never block save because a field is empty
3. Lead detail page (/leads/[id]):
   - Header: business name, score badge, status, owner, source
   - All fields editable inline
   - Timeline sidebar
   - Notes section
4. CSV import wizard (/leads/import):
   - Upload → preview → column mapping → import → results
5. Lead dashboard widgets:
   - Total leads, by status, by source, avg score

DATABASE:
- leads table with all indexes (see DATABASE_ARCHITECTURE.md)
- lead_score_history, lead_imports
- Search vector trigger

ACCEPTANCE CRITERIA:
- [ ] Create, read, update, delete leads with all fields
- [ ] Filter and sort lead list
- [ ] Kanban board view by status
- [ ] CSV import with column mapping works for 1000+ rows
- [ ] Lead scoring (manual + AI) with history
- [ ] Lead assignment (single + bulk)
- [ ] Tags with autocomplete
- [ ] Lead appears in global search
- [ ] Activity timeline shows all lead events
- [ ] No required fields block lead creation
```

---

# PHASE 3 — One-Page CRM

## Prompt

```
Implement Phase 3: One-Page CRM for Axorks OS.

PREREQUISITE: Phase 2 complete and verified.

GOAL: Build the unified CRM view — one page, no tabs, everything visible.

DESIGN PRINCIPLE: When viewing any CRM entity (lead, company, contact, deal), ALL related information is visible on ONE scrollable page. No tabs. No hidden panels.

BACKEND:
1. Companies CRUD: /api/v1/companies
2. Contacts CRUD: /api/v1/contacts (linked to companies)
3. Deals CRUD: /api/v1/deals (linked to companies, contacts, leads)
4. Polymorphic resources (work for any entity_type + entity_id):
   - Notes: POST/GET/PATCH/DELETE /api/v1/notes
   - Calls: POST/GET /api/v1/calls
   - Emails: POST/GET /api/v1/emails
   - Files: POST/GET/DELETE /api/v1/files (upload to Cloudinary)
5. Unified timeline:
   - GET /api/v1/{entity_type}/{entity_id}/timeline
   - Aggregates: activities, notes, calls, emails, status changes, assignments
6. Lead → Company conversion:
   - POST /api/v1/leads/{id}/convert — creates company + contact from lead
7. Relationship queries:
   - GET /api/v1/companies/{id}/contacts
   - GET /api/v1/companies/{id}/deals
   - GET /api/v1/companies/{id}/projects (stub for Phase 6)
   - GET /api/v1/companies/{id}/invoices (stub for Phase 9)

FRONTEND — One-Page CRM Layout:
```
┌─────────────────────────────────────────────────────────┐
│ HEADER: Entity name, status badge, owner, actions       │
├─────────────────────────────────────┬───────────────────┤
│ MAIN CONTENT (scrollable)           │ TIMELINE (sticky) │
│                                     │                   │
│ ▸ Key Details (inline editable)     │ Today             │
│ ▸ Contact Info                      │  - Call logged     │
│ ▸ Company Info                      │  - Email sent      │
│ ▸ Deal Info (value, stage, close)   │  - Note added      │
│ ▸ Projects (linked)                 │ Yesterday          │
│ ▸ Invoices (linked)                 │  - Status changed  │
│ ▸ Notes (add + list)                │  - Lead created    │
│ ▸ Calls (log + list)                │                   │
│ ▸ Emails (list)                     │                   │
│ ▸ Files (upload + list)             │                   │
│ ▸ Tasks (linked)                    │                   │
│ ▸ Meetings (linked)                 │                   │
│ ▸ Contracts (linked)                │                   │
│ ▸ Tags                              │                   │
└─────────────────────────────────────┴───────────────────┘
```

Components:
1. CRMOnePageView — reusable layout for any entity type
2. InlineEditableField — click to edit any field
3. TimelineFeed — chronological activity stream
4. NotesPanel — add/view/pin notes
5. CallsPanel — log calls with duration, outcome, optional recording URL
6. FilesPanel — drag-drop upload, file list with preview
7. RelatedEntities — shows linked projects, invoices, deals
8. QuickActions — floating action button: add note, log call, send email, upload file

PAGES:
- /crm/companies — company list
- /crm/companies/[id] — one-page company CRM
- /crm/contacts/[id] — one-page contact CRM
- /crm/deals/[id] — one-page deal CRM
- /leads/[id] — upgraded to full one-page CRM (from Phase 2)

ACCEPTANCE CRITERIA:
- [ ] Company, contact, deal CRUD
- [ ] One-page view shows ALL sections without tabs
- [ ] Inline editing works for all fields
- [ ] Notes, calls, emails, files attach to any entity
- [ ] Timeline shows all activity chronologically
- [ ] Lead conversion to company + contact
- [ ] File upload to Cloudinary works
- [ ] Related entities displayed (deals on company, etc.)
- [ ] No page navigation needed to see all CRM data
```

---

# PHASE 4 — AI Sales Assistant

## Prompt

```
Implement Phase 4: AI Sales Assistant for Axorks OS.

PREREQUISITE: Phase 3 complete. AI Architecture doc read.

GOAL: Build the AI assistant that helps during sales conversations and automates CRM updates.

BACKEND — AI Infrastructure:
1. AI Provider layer (see AI_ARCHITECTURE.md):
   - AIProvider abstract base class
   - OpenAI, Anthropic, Gemini, DeepSeek implementations
   - AIProviderRouter with task-based defaults
   - AIConfig, AIResponse models
2. AI Service:
   - complete(), stream(), embed(), classify()
   - Context builder (scoped to tenant, entity snapshot)
   - Token usage logging (ai_usage_logs table)
3. Prompt management:
   - System prompts stored in ai_prompts table
   - Jinja2 template rendering
4. Action confirmation:
   - ai_action_confirmations table
   - POST /ai/actions → create pending action
   - POST /ai/actions/{id}/confirm → execute
   - POST /ai/actions/{id}/reject → discard

BACKEND — Sales Assistant Endpoints:
1. POST /api/v1/ai/sales/suggest-questions — given lead/deal context
2. POST /api/v1/ai/sales/summarize — summarize conversation/call/notes
3. POST /api/v1/ai/sales/detect-requirements — extract requirements from text
4. POST /api/v1/ai/sales/estimate-budget — budget range from requirements
5. POST /api/v1/ai/sales/estimate-complexity — T-shirt size + hours
6. POST /api/v1/ai/sales/suggest-tech — technology recommendations
7. POST /api/v1/ai/sales/suggest-followup — follow-up email/message draft
8. POST /api/v1/ai/sales/detect-objections — objection + response suggestion
9. POST /api/v1/ai/sales/action-items — extract action items from conversation
10. POST /api/v1/ai/sales/update-crm — suggest CRM updates (requires confirmation)
11. POST /api/v1/ai/stream — SSE streaming for all above

FRONTEND:
1. AISalesPanel — side panel on CRM one-page view:
   - "Ask AI" input
   - Contextual suggestion chips based on entity state
   - Streaming response display
2. AISuggestionCard — individual suggestion with accept/dismiss
3. AIConfirmationCard — preview CRM changes before applying
4. Inline AI actions on CRM pages:
   - "Summarize" button on notes/calls section
   - "Detect Requirements" on call transcripts
   - "Suggest Follow-up" after calls
   - "Estimate Budget" when requirements exist
5. AI conversation history per entity

RULES:
- AI NEVER auto-executes CRM updates — always confirmation
- AI responses include reasoning
- AI context scoped to current entity only
- All AI calls logged with tokens and cost

ACCEPTANCE CRITERIA:
- [ ] AI provider abstraction works with at least OpenAI + Anthropic
- [ ] Sales assistant suggests questions for a lead
- [ ] Summarize works on notes/call transcripts
- [ ] Requirement detection extracts structured requirements
- [ ] Budget and complexity estimation return reasoned estimates
- [ ] Follow-up email draft generated
- [ ] Objection detection with response suggestions
- [ ] Action items extracted and creatable as tasks (with confirmation)
- [ ] CRM update suggestions require explicit confirmation
- [ ] Streaming responses work in UI
- [ ] Token usage logged per request
```

---

# PHASE 5 — Proposal Generator

## Prompt

```
Implement Phase 5: Proposal Generator for Axorks OS.

PREREQUISITE: Phase 4 complete.

GOAL: Auto-generate proposals, quotations, SOWs, contracts from CRM data and AI.

BACKEND:
1. Proposals CRUD: /api/v1/proposals
2. Proposal types: proposal, quotation, sow, contract, technical_proposal
3. Proposal content stored as structured JSONB:
   - sections: [{ title, content, order }]
   - pricing: { items: [{ description, quantity, unit_price, amount }], subtotal, tax, total }
   - timeline: { milestones: [{ title, description, start_date, end_date, deliverables }] }
   - payment_plan: { milestones: [{ title, amount, due_date, percentage }] }
   - terms_and_conditions: string
4. AI generation:
   - POST /api/v1/proposals/generate — AI generates full proposal from lead/deal context
   - Input: entity_id, proposal_type, template_id (optional), additional_notes
   - Uses AI provider layer with proposal-specific prompts
5. Templates:
   - CRUD /api/v1/proposal-templates
   - Organization-level templates with default sections
6. Version history:
   - entity_versions table — snapshot on every save
7. PDF export:
   - POST /api/v1/proposals/{id}/export/pdf — generate PDF via background job
   - Use WeasyPrint or similar
8. Word export:
   - POST /api/v1/proposals/{id}/export/docx
9. Send proposal:
   - POST /api/v1/proposals/{id}/send — email via Resend + mark sent
10. Proposal milestones: CRUD linked to proposal

FRONTEND:
1. /proposals — list with status filters (draft, sent, accepted, rejected)
2. /proposals/new — creation wizard:
   - Select deal/company → select type → AI generate or blank → edit
3. /proposals/[id] — rich editor:
   - Section-based editor (Notion-like blocks)
   - Pricing table editor
   - Timeline/milestone editor
   - Payment plan editor
   - AI assist buttons: "Improve section", "Add section", "Adjust pricing"
   - Preview mode
   - Export PDF / Word buttons
   - Send button
4. Template management in settings

ACCEPTANCE CRITERIA:
- [ ] Create proposal manually and via AI generation
- [ ] All proposal types supported
- [ ] Section-based editor works
- [ ] Pricing table calculates totals
- [ ] Timeline and payment plan editable
- [ ] PDF export generates formatted document
- [ ] Version history tracks changes
- [ ] Send proposal via email
- [ ] Templates reusable across proposals
```

---

# PHASE 6 — Project Management

## Prompt

```
Implement Phase 6: Project Management for Axorks OS.

PREREQUISITE: Phase 5 complete.

GOAL: Full project management — Kanban, sprints, backlog, roadmap, time tracking.

BACKEND:
- Projects CRUD (linked to companies, deals, proposals)
- Sprints CRUD
- Tasks CRUD with hierarchy (epic → story → task → subtask)
- Task dependencies
- Time entries CRUD
- Views: board (by status), backlog (by priority), sprint, roadmap (by date), gantt (computed)

FRONTEND:
- /projects — project list
- /projects/[id]/board — Kanban with drag-and-drop (Framer Motion)
- /projects/[id]/backlog — prioritized backlog
- /projects/[id]/sprints — sprint planning and burndown
- /projects/[id]/roadmap — timeline roadmap
- /projects/[id]/gantt — Gantt chart
- /projects/[id]/calendar — calendar view
- Task detail panel (slide-over, not separate page)
- Time tracking widget on tasks
- Quick create task (Cmd+Shift+T)

ACCEPTANCE CRITERIA:
- [ ] Project CRUD linked to CRM entities
- [ ] Kanban board with drag-and-drop status changes
- [ ] Task hierarchy (epic/story/task/subtask)
- [ ] Sprint planning and burndown chart
- [ ] Time entries logged against tasks
- [ ] Gantt chart renders dependencies
- [ ] Roadmap view shows project timeline
```

---

# PHASE 7 — Development Hub

## Prompt

```
Implement Phase 7: Development Hub for Axorks OS.

PREREQUISITE: Phase 6 complete.

GOAL: Connect GitHub/GitLab/Bitbucket — repos, PRs, issues, deployments visible in Axorks OS.

BACKEND:
- OAuth connect for GitHub, GitLab, Bitbucket
- Sync repositories, pull requests, issues, deployments
- Webhook receivers for real-time updates
- Link repos to projects
- Environment variable management (encrypted storage)

FRONTEND:
- /dev — Dev Hub dashboard
- /dev/repos/[id] — repo detail with PRs, issues, deployments
- PR review summary (AI-generated)
- Deployment status indicators
- Link repo to project flow

ACCEPTANCE CRITERIA:
- [ ] GitHub OAuth connect and repo sync
- [ ] PRs and issues displayed
- [ ] Deployments tracked
- [ ] Repos linkable to projects
- [ ] Webhook updates in real-time
```

---

# PHASE 8 — Client Portal

## Prompt

```
Implement Phase 8: Client Portal for Axorks OS.

PREREQUISITE: Phase 6 complete (projects needed).

GOAL: Clients login and see their projects, invoices, documents, progress.

BACKEND:
- Portal user auth (separate from internal auth, role: client)
- Scoped access: client sees ONLY their company's data
- Portal endpoints: projects, invoices, documents, messages, approvals, support tickets

FRONTEND:
- Separate layout at /portal/*
- /portal — client dashboard
- /portal/projects/[id] — project progress view
- /portal/invoices — invoice list with pay button
- /portal/documents — shared documents
- /portal/messages — messaging with team
- /portal/support — support ticket submission
- Clean, branded UI (organization logo/colors)

ACCEPTANCE CRITERIA:
- [ ] Client can login to portal
- [ ] Client sees only their company's data
- [ ] Project progress visible
- [ ] Invoices viewable
- [ ] Document sharing works
- [ ] Support ticket submission works
```

---

# PHASE 9 — Finance

## Prompt

```
Implement Phase 9: Finance for Axorks OS.

PREREQUISITE: Phase 5 (proposals) and Phase 8 (portal payments).

GOAL: Invoices, expenses, revenue tracking, cash flow forecast.

BACKEND:
- Invoices CRUD with line items, auto-numbering
- Expenses CRUD with categories
- Revenue aggregation
- Payment recording (manual + Stripe webhook)
- Recurring invoice schedules
- Financial reports: P&L, cash flow, revenue by client/project

FRONTEND:
- /finance/invoices — invoice list and detail
- /finance/expenses — expense tracking
- /finance/dashboard — revenue, profit, cash flow charts
- /finance/forecast — cash flow forecast
- Invoice creation from proposal/deal
- PDF invoice generation

ACCEPTANCE CRITERIA:
- [ ] Invoice CRUD with line items
- [ ] Expense tracking
- [ ] Revenue dashboard with charts
- [ ] Invoice PDF generation
- [ ] Payment recording
- [ ] Cash flow forecast
```

---

# PHASE 10 — Knowledge Base

## Prompt

```
Implement Phase 10: Knowledge Base.

GOAL: Internal wiki, SOPs, coding standards, meeting notes, prompt library, templates.
- Rich text editor (Notion-like blocks)
- Nested pages, search, templates
- Prompt library for AI prompts
- /knowledge, /knowledge/[slug]
```

---

# PHASE 11 — Marketing

## Prompt

```
Implement Phase 11: Marketing.

GOAL: Campaign management, content calendar, analytics dashboard, email marketing, funnels.
- Google Analytics / Search Console integration
- Campaign CRUD, content calendar
- Email campaign builder (via Resend)
- Lead funnel visualization
```

---

# PHASE 12 — Recruitment

## Prompt

```
Implement Phase 12: Recruitment.

GOAL: Candidate pipeline, CV parser (AI), interview notes, assessments, offer letters, onboarding.
- Candidate CRUD with pipeline stages
- AI CV parsing
- Interview scheduling and notes
- Assessment templates
- Offer letter generation
```

---

# PHASE 13 — HR

## Prompt

```
Implement Phase 13: HR.

GOAL: Employee directory, attendance, leaves, payroll, performance reviews, goals, training.
- Employee profiles linked to user accounts
- Leave management workflow
- Basic payroll tracking
- Performance review cycles
```

---

# PHASE 14 — Automation Engine

## Prompt

```
Implement Phase 14: Automation Engine for Axorks OS.

PREREQUISITE: Phases 1-5 complete.

GOAL: Visual no-code automation — trigger → condition → action.

BACKEND:
- Workflows CRUD with trigger/condition/action steps
- Trigger types: entity events (lead.created, deal.won, etc.), schedule (cron)
- Condition types: field equals, field contains, score greater than, etc.
- Action types: assign, send email, create task, update field, webhook, AI generate, notify Slack
- Execution engine: event → match workflows → evaluate conditions → execute actions
- Execution log with retry and idempotency

FRONTEND:
- /automations — workflow list
- /automations/[id] — visual workflow builder (node-based UI)
- Pre-built templates: "New lead → assign → email → reminder"
- Execution log viewer

ACCEPTANCE CRITERIA:
- [ ] Create workflow with trigger + conditions + actions
- [ ] Workflow executes on lead.created event
- [ ] Email action sends via Resend
- [ ] Assign action updates lead owner
- [ ] Execution log shows step-by-step results
- [ ] Visual builder is intuitive (no code required)
```

---

# PHASE 15 — AI Everywhere

## Prompt

```
Implement Phase 15: AI Everywhere for Axorks OS.

PREREQUISITE: Phase 4 (AI infrastructure) complete.

GOAL: Add contextual AI actions to EVERY screen in Axorks OS.

For each existing screen, add inline AI actions:
- Text fields: Summarize, Improve, Translate, Expand
- Lists: "Analyze trends", "Suggest priorities"
- CRM records: "Predict close date", "Suggest upsell"
- Projects: "Sprint summary", "Risk detection"
- Emails: "Rewrite", "Change tone"
- Search: Natural language → structured filters
- Dashboards: "Explain this chart", "What should I focus on?"

Components (packages/ui/src/ai/):
- AIInlineActions, AISuggestionPanel, AIStreamingText, AIComposerAssist

RULES:
- AI actions appear as subtle icon buttons, not modals
- Streaming for long responses
- Confirmation for any data mutation
- Context scoped to current page/entity

ACCEPTANCE CRITERIA:
- [ ] AI inline actions on CRM, projects, finance, knowledge pages
- [ ] Natural language search works
- [ ] Dashboard AI insights generate
- [ ] Email compose AI assist works
- [ ] No separate "AI page" exists — AI is everywhere
```

---

# PHASE 16 — Analytics

## Prompt

```
Implement Phase 16: Analytics Dashboards.

GOAL: Visual dashboards for company, sales, finance, marketing, projects, support, leads.
- Configurable widgets (charts, KPIs, tables)
- Date range filters
- Drill-down capability
- /analytics/[dashboard]
```

---

# PHASE 17 — Integrations

## Prompt

```
Implement Phase 17: Integrations.

GOAL: Connect external services via OAuth and webhooks.

Priority integrations:
- Google Workspace (Gmail, Calendar, Drive)
- Microsoft 365
- GitHub, GitLab, Bitbucket
- Slack, Discord
- WhatsApp Business API
- Stripe, PayPal
- Resend
- OpenAI, Anthropic, Google AI, DeepSeek
- LinkedIn, Facebook, Instagram, YouTube (compliant data access)
- Google Analytics, Search Console

Pattern: OAuth connect → store encrypted tokens → sync → webhooks → domain events
- /integrations — integration marketplace UI
- Per-integration connect/disconnect/sync settings
```

---

# PHASE 18 — Mobile / PWA

## Prompt

```
Implement Phase 18: Mobile / PWA.

GOAL: Responsive, installable PWA with offline support.

- Service worker for offline caching
- Web app manifest for installability
- Push notifications
- Responsive layouts for all existing pages
- Mobile-specific: camera upload, voice notes, document scanning
- Touch-optimized interactions
- Bottom navigation on mobile

ACCEPTANCE CRITERIA:
- [ ] Installable as PWA on iOS and Android
- [ ] Core pages work offline (view cached data)
- [ ] Push notifications delivered
- [ ] All pages responsive down to 320px
- [ ] Camera upload works on mobile
```

---

*Complete each phase fully before starting the next. Reference architecture docs for all technical decisions.*
