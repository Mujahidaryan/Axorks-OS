# Axorks OS — Phase 0 Product Engineering Deliverables

> Product Vision, PRD, Requirements, Personas, IA, MVP Scope

---

## 1. Product Vision

**Axorks OS** is the AI-powered operating system for software agencies and consulting companies. One system to run an entire software company — sales, delivery, finance, HR, marketing, and client collaboration — with a premium, minimal, keyboard-driven, AI-first experience.

**Not** Salesforce. **Not** HubSpot. **Not** Monday.

**Instead:** Apple × Linear × Notion × Vercel × ChatGPT.

---

## 2. Problem Statement

Software agencies and consultancies today operate across 10–20 disconnected tools:

- CRM (HubSpot/Salesforce) for sales
- Project management (Jira/Linear) for delivery
- Invoicing (FreshBooks/QuickBooks) for finance
- Slack/Email for communication
- Google Docs/Notion for knowledge
- GitHub for development
- Spreadsheets for everything else

**Pain points:**
- Context switching kills productivity
- Data lives in silos — no single source of truth
- AI tools are disconnected from business data
- Client experience is fragmented (separate portals, emails, invoices)
- Onboarding new team members requires learning 15+ tools
- No unified view of company health

---

## 3. Solution

One operating system where every workflow — from first lead touch to final invoice payment — happens in a cohesive, beautiful, fast product with AI assistance at every step.

---

## 4. Target Market

| Segment | Description |
|---------|-------------|
| **Primary** | Software development agencies (5–50 people) |
| **Secondary** | AI consultancies and digital engineering firms |
| **Tertiary** | Freelance collectives scaling to agencies |
| **Future SaaS** | Any consulting/agency company globally |

---

## 5. User Personas

### Persona 1: Alex — Agency Founder / CEO

- **Age:** 32–45
- **Role:** Runs a 15-person software agency
- **Goals:** See company health at a glance, close more deals, deliver on time, maintain profitability
- **Pain:** Drowning in tools, no unified dashboard, can't see pipeline + delivery + finance together
- **Uses:** Dashboard, CRM, Finance, Analytics, AI Sales Assistant
- **Success metric:** "I open Axorks OS and I know exactly where my company stands"

### Persona 2: Sarah — Sales Lead

- **Age:** 26–38
- **Role:** Head of business development
- **Goals:** Manage pipeline, qualify leads fast, send proposals quickly, hit revenue targets
- **Pain:** Manual lead research, slow proposal creation, no AI assistance during calls
- **Uses:** Lead Intelligence, CRM, AI Sales Assistant, Proposal Generator, Automation
- **Success metric:** "I can go from lead to proposal in under 30 minutes"

### Persona 3: Marcus — Project Manager

- **Age:** 28–40
- **Role:** Delivery lead managing 3–5 concurrent projects
- **Goals:** Keep projects on track, manage sprints, track time, communicate with clients
- **Pain:** Jira is overkill, client updates are manual, time tracking is forgotten
- **Uses:** Project Management, Client Portal, Time Tracking, Dev Hub
- **Success metric:** "My clients see progress without me sending weekly emails"

### Persona 4: Priya — Developer

- **Age:** 24–35
- **Role:** Full-stack developer on client projects
- **Goals:** Clear tasks, linked repos, minimal overhead, focus on coding
- **Pain:** Context switching between GitHub, Jira, Slack, and CRM
- **Uses:** Tasks, Dev Hub (PRs, deployments), Knowledge Base, Time Tracking
- **Success metric:** "I see my tasks, my PRs, and project context in one place"

### Persona 5: David — Client (External)

- **Age:** 35–55
- **Role:** CTO at a client company
- **Goals:** See project progress, approve milestones, pay invoices, access documents
- **Pain:** Email chains, PDF invoices, no visibility into development progress
- **Uses:** Client Portal only
- **Success metric:** "I log in and see everything about my project without calling anyone"

### Persona 6: Nina — HR Manager

- **Age:** 30–42
- **Role:** People operations at a growing agency
- **Goals:** Hire talent, manage employees, track attendance, run payroll
- **Pain:** Separate HR tools, manual onboarding, no integration with project staffing
- **Uses:** Recruitment, HR, Knowledge Base (SOPs)
- **Success metric:** "From job posting to onboarded employee in one system"

---

## 6. Competitive Analysis

| Competitor | Strengths | Weaknesses | Axorks OS Advantage |
|------------|-----------|------------|---------------------|
| **Salesforce** | Enterprise CRM, ecosystem | Complex, expensive, not agency-focused | Simpler, AI-native, full OS not just CRM |
| **HubSpot** | Marketing + CRM | Not built for project delivery | Unified sales → delivery → finance |
| **Monday.com** | Visual PM | Weak CRM, no AI depth, no finance | Deeper AI, one-page CRM, finance built-in |
| **Linear** | Beautiful PM, fast | No CRM, no finance, no client portal | Full company OS with Linear-quality UX |
| **Notion** | Flexible docs/wiki | Not structured for CRM/projects/finance | Purpose-built workflows with Notion-like editing |
| **FreshBooks** | Simple invoicing | No CRM, no projects | Everything connected |
| **Copper** | Google-integrated CRM | Limited PM/finance | Complete operating system |

**Positioning:** Axorks OS occupies the whitespace — no product combines CRM + PM + Finance + Dev Hub + Client Portal + AI with premium UX for agencies.

---

## 7. Functional Requirements

### FR-1: Multi-Tenant Organization Management
- Create/manage organizations and workspaces
- Invite members with role-based permissions
- Organization-level settings and branding

### FR-2: Lead Intelligence
- Capture leads from 12+ sources (manual, CSV, API, social, directories)
- Lead scoring (manual + AI-assisted)
- Lead assignment and pipeline management
- Bulk import with validation

### FR-3: One-Page CRM
- Single view showing client, leads, projects, invoices, emails, calls, notes, contracts, files, tasks, meetings, timeline
- No tabs — everything visible and scrollable
- Inline editing for all fields
- Activity timeline with all interactions

### FR-4: AI Sales Assistant
- Real-time suggestions during sales conversations
- Requirement detection and budget estimation
- Objection handling suggestions
- Auto-generate follow-ups and action items
- CRM updates with confirmation

### FR-5: Proposal Generator
- Generate proposals, quotations, SOWs, contracts from CRM data
- Architecture documents and technical proposals
- Timeline, milestones, payment plans
- Export to PDF and Word

### FR-6: Project Management
- Kanban, sprint, backlog, roadmap views
- Epics, stories, tasks, subtasks with dependencies
- Time tracking, Gantt chart, burndown, calendar
- File attachments and comments

### FR-7: Development Hub
- Connect GitHub/GitLab/Bitbucket repositories
- View PRs, issues, deployments, CI/CD status
- Environment variable management
- Link repos to projects

### FR-8: Client Portal
- Client login with scoped access
- View projects, invoices, documents, progress
- Approve milestones, submit support tickets
- Message team, schedule meetings, make payments

### FR-9: Finance
- Invoices, expenses, revenue tracking
- Profit/loss, taxes, subscriptions
- Recurring billing and payment milestones
- Cash flow forecast

### FR-10: Knowledge Base
- Company SOPs, coding standards, meeting notes
- Internal wiki with rich editing
- Prompt library and document templates

### FR-11: Marketing
- Website analytics, SEO dashboard
- Campaign management, content calendar
- Email marketing, lead funnels

### FR-12: Recruitment & HR
- Candidate pipeline with CV parsing
- Interview notes, assessments, offer letters
- Employee management, attendance, leaves, payroll

### FR-13: Automation Engine
- Visual trigger → condition → action builder
- No-code workflow automation
- Pre-built templates for common agency workflows

### FR-14: AI Everywhere
- Contextual AI on every screen
- Summarize, rewrite, translate, generate, predict, classify, extract, suggest

### FR-15: Analytics Dashboards
- Company, sales, finance, marketing, projects, support, lead dashboards
- Visual charts with drill-down

### FR-16: Integrations
- Google, Microsoft, GitHub, GitLab, Slack, Discord, WhatsApp, Stripe, PayPal, Resend, AI providers, social platforms

### FR-17: Global Search & Command Palette
- Search across all entities
- Cmd+K command palette for navigation and actions
- Keyboard shortcuts throughout

### FR-18: Mobile / PWA
- Responsive design, installable PWA
- Offline support, push notifications
- Camera, voice notes, document scanning

---

## 8. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Page load (LCP) | < 2.5 seconds |
| NFR-2 | API response (p95) | < 300ms (non-AI endpoints) |
| NFR-3 | AI first token | < 1.5 seconds |
| NFR-4 | Uptime | 99.9% |
| NFR-5 | Concurrent users | 500 per organization |
| NFR-6 | Data scale | 10M leads, 100K companies |
| NFR-7 | Accessibility | WCAG 2.2 AA |
| NFR-8 | Browser support | Chrome, Firefox, Safari, Edge (last 2 versions) |
| NFR-9 | Mobile | Responsive + PWA |
| NFR-10 | Localization | i18n-ready (English first) |
| NFR-11 | Dark/Light mode | System preference + manual toggle |
| NFR-12 | Backup RPO/RTO | 1 hour / 4 hours |
| NFR-13 | Security | OWASP Top 10, 2FA, encryption |
| NFR-14 | Audit | All mutations logged with user/IP/timestamp |

---

## 9. Information Architecture

```
Axorks OS
├── 🏠 Home / Dashboard
├── 🔍 Search (Cmd+K)
├── 📊 Analytics
│   ├── Company Overview
│   ├── Sales
│   ├── Finance
│   ├── Marketing
│   ├── Projects
│   └── Leads
├── 🎯 Leads
│   ├── All Leads (list/board)
│   ├── Lead Detail
│   ├── Import
│   └── Sources
├── 👥 CRM
│   ├── Companies
│   ├── Contacts
│   ├── Deals
│   └── One-Page CRM View (/{entity}/{id})
├── 🤖 AI Assistant
│   └── (inline everywhere — not a separate page)
├── 📄 Proposals
│   ├── All Proposals
│   ├── Create / Edit
│   └── Templates
├── 📋 Projects
│   ├── All Projects
│   ├── Board (Kanban)
│   ├── Backlog
│   ├── Sprints
│   ├── Roadmap
│   ├── Gantt
│   └── Calendar
├── 💻 Dev Hub
│   ├── Repositories
│   ├── Pull Requests
│   ├── Deployments
│   └── Environments
├── 🌐 Client Portal (separate auth)
│   ├── Projects
│   ├── Invoices
│   ├── Documents
│   ├── Messages
│   └── Support
├── 💰 Finance
│   ├── Invoices
│   ├── Expenses
│   ├── Revenue
│   ├── Subscriptions
│   └── Forecast
├── 📚 Knowledge
│   ├── Wiki
│   ├── SOPs
│   ├── Templates
│   └── Prompt Library
├── 📣 Marketing
│   ├── Campaigns
│   ├── Content Calendar
│   ├── Analytics
│   └── Funnels
├── 👔 Recruitment
│   ├── Candidates
│   ├── Interviews
│   └── Offers
├── 🏢 HR
│   ├── Employees
│   ├── Attendance
│   ├── Leaves
│   └── Payroll
├── ⚡ Automations
│   ├── Workflows
│   └── Execution Log
├── 🔌 Integrations
├── ⚙️ Settings
│   ├── Organization
│   ├── Workspace
│   ├── Team & Roles
│   ├── Billing (future)
│   ├── Preferences
│   ├── Keyboard Shortcuts
│   └── Security
└── 👤 Profile
```

---

## 10. User Journeys

### Journey 1: Lead to Closed Deal

```
Lead arrives (LinkedIn/manual/CSV)
  → AI scores and enriches lead
  → Sales assigns and contacts
  → AI assists during discovery call
  → Requirements detected, budget estimated
  → Proposal auto-generated
  → Client reviews in portal
  → Deal won → Project auto-created
  → Invoice milestone scheduled
```

### Journey 2: Project Delivery

```
Project created from won deal
  → Tasks imported from proposal scope
  → Sprint planned on Kanban board
  → Dev links GitHub repo
  → PRs and deployments visible in Dev Hub
  → Client sees progress in portal
  → Time tracked against tasks
  → Milestone completed → invoice generated
  → Client pays via portal
```

### Journey 3: Daily Agency Operations

```
Team member opens Axorks OS
  → Dashboard shows KPIs
  → Cmd+K → jump to any entity
  → Check notifications
  → Update task status
  → Log time entry
  → AI summarizes standup
  → Review automation executions
```

---

## 11. Sitemap (URL Structure)

```
/                           → Dashboard
/search                     → Global search results
/leads                      → Lead list
/leads/new                  → Create lead
/leads/[id]                 → Lead detail (one-page CRM)
/crm/companies              → Company list
/crm/companies/[id]         → Company one-page CRM
/crm/contacts/[id]          → Contact one-page CRM
/crm/deals/[id]             → Deal one-page CRM
/proposals                  → Proposal list
/proposals/new              → Create proposal
/proposals/[id]             → Proposal editor
/projects                   → Project list
/projects/[id]              → Project detail
/projects/[id]/board        → Kanban board
/projects/[id]/backlog      → Backlog
/projects/[id]/sprints      → Sprint view
/projects/[id]/roadmap      → Roadmap
/projects/[id]/gantt        → Gantt chart
/dev                        → Dev Hub overview
/dev/repos/[id]             → Repository detail
/finance/invoices           → Invoice list
/finance/invoices/[id]      → Invoice detail
/finance/expenses           → Expense list
/knowledge                  → Wiki home
/knowledge/[slug]           → Article
/marketing/campaigns        → Campaign list
/recruitment/candidates     → Candidate pipeline
/hr/employees               → Employee directory
/automations                → Workflow list
/automations/[id]           → Workflow builder
/integrations               → Integration settings
/analytics/[dashboard]      → Analytics dashboards
/settings/*                 → Settings pages
/portal/*                   → Client portal (separate layout)
/auth/login                 → Login
/auth/register              → Register (future SaaS)
```

---

## 12. Feature Prioritization (MoSCoW)

### Must Have (MVP — Phases 0–5)

- Foundation (auth, RBAC, orgs, search, command palette)
- Lead Intelligence (capture, score, assign, import)
- One-Page CRM (companies, contacts, deals, timeline)
- AI Sales Assistant (basic suggestions, summaries)
- Proposal Generator (basic proposal + PDF export)

### Should Have (Phases 6–9)

- Project Management (Kanban, tasks, time tracking)
- Development Hub (GitHub integration)
- Client Portal (view projects, invoices, documents)
- Finance (invoices, expenses, basic reporting)

### Could Have (Phases 10–14)

- Knowledge Base
- Marketing dashboard
- Recruitment
- HR
- Automation Engine

### Won't Have (Initial — Phases 15–18)

- AI Everywhere (full rollout — incremental from Phase 4)
- Full analytics suite
- All integrations
- Mobile PWA with offline

---

## 13. MVP Scope

**Timeline estimate:** 8–12 weeks for solo/small team

**MVP includes:**
1. ✅ Auth + RBAC + Organizations + Workspaces
2. ✅ Global search + Command palette (Cmd+K)
3. ✅ Dark/light mode + preferences
4. ✅ Lead CRUD + import (CSV) + scoring + assignment
5. ✅ One-page CRM view (lead/company/deal)
6. ✅ Notes, calls, emails, files, timeline on CRM records
7. ✅ AI Sales Assistant (suggestions, summaries, requirement detection)
8. ✅ Proposal generator (basic) + PDF export
9. ✅ Notifications + activity/audit logs

**MVP excludes:**
- Project management (Phase 6)
- Dev Hub (Phase 7)
- Client portal (Phase 8)
- Finance (Phase 9)
- Full automation engine (Phase 14)

---

## 14. Future Scope

- Full project management with Gantt, sprints, burndown
- GitHub/GitLab/Bitbucket Dev Hub
- Client portal with payments
- Complete finance module with forecasting
- Knowledge base and prompt library
- Marketing analytics and campaigns
- Recruitment and HR modules
- Visual automation engine
- AI on every screen
- Full analytics dashboards
- 20+ integrations
- Mobile PWA with offline
- Commercial SaaS with billing, self-serve signup
- White-label client portals
- Marketplace for templates and integrations
- SOC 2 compliance

---

## 15. Success Metrics

| Metric | Target (6 months post-MVP) |
|--------|---------------------------|
| Daily active users (internal) | 100% of Axorks team |
| Lead-to-proposal time | < 30 minutes |
| Tools replaced | ≥ 5 external tools |
| User satisfaction (NPS) | > 50 |
| System uptime | > 99.9% |
| Page load time | < 2.5s LCP |

---

*Phase 0 complete. Proceed to Phase 1 implementation.*
