# Axorks OS

**The AI-powered operating system for software agencies and consulting companies.**

Axorks OS is not a CRM. It is a proprietary company operating system — one cohesive product where everything required to run a modern software company lives in a single, premium, keyboard-driven, AI-first experience.

---

## Vision

> Apple × Linear × Notion × Vercel × ChatGPT — built for software houses, AI consultancies, and digital engineering firms.

Everything from lead intelligence to proposals, projects, development, finance, HR, and client portals — without switching applications.

---

## Documentation

| Document | Purpose |
|----------|---------|
| [**Master Prompt**](docs/AXORKS_OS_MASTER_PROMPT.md) | **Start here.** Single executive prompt for any coding AI |
| [System Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md) | Full technical architecture and engineering decisions |
| [Database Architecture](docs/architecture/DATABASE_ARCHITECTURE.md) | Schema design, multi-tenancy, scaling strategy |
| [Security Architecture](docs/architecture/SECURITY_ARCHITECTURE.md) | Auth, RBAC, encryption, compliance |
| [AI Architecture](docs/architecture/AI_ARCHITECTURE.md) | Provider abstraction, AI-everywhere design |
| [Phase 0 Deliverables](docs/product/PHASE_0_DELIVERABLES.md) | PRD, personas, IA, competitive analysis, MVP scope |
| [Phase Prompts (1–18)](docs/phases/PHASE_PROMPTS.md) | Implementation prompts for each build phase |

---

## Recommended Monorepo Structure

```
axorks-os/
├── apps/
│   ├── web/          # Next.js 15 frontend (Vercel)
│   └── api/          # FastAPI backend (Railway)
├── packages/
│   ├── ui/           # Shared shadcn/ui components
│   ├── types/        # Shared TypeScript types + OpenAPI client
│   ├── database/     # Alembic migrations, shared schemas
│   └── utils/        # Shared utilities
├── docs/             # Architecture, product, phase prompts
├── scripts/          # Dev and deployment scripts
├── docker/           # Docker Compose for local dev
└── .github/          # CI/CD workflows
```

---

## Tech Stack (Recommended)

| Layer | Choice |
|-------|--------|
| Frontend | Next.js 15, TypeScript, Tailwind, shadcn/ui, TanStack Query |
| Backend | **FastAPI** (Python) — AI ecosystem, performance, OpenAPI |
| Database | PostgreSQL (Neon) + SQLAlchemy 2.0 + Alembic |
| Cache | Redis (Upstash) |
| Auth | Better Auth or Clerk |
| AI | Provider abstraction (OpenAI, Anthropic, Gemini, DeepSeek) |
| Email | Resend |
| Storage | Cloudinary → Cloudflare R2 |
| Monitoring | Sentry, PostHog, Axiom |

---

## Build Order

```
Phase 0  → Product Engineering
Phase 1  → Foundation (Auth, RBAC, Search, Command Palette)
Phase 2  → Lead Intelligence
Phase 3  → One-Page CRM
Phase 4  → AI Sales Assistant
Phase 5  → Proposal Generator
Phase 6  → Project Management
Phase 7  → Development Hub
Phase 8  → Client Portal
Phase 9  → Finance
Phase 10 → Knowledge Base
Phase 11 → Marketing
Phase 12 → Recruitment
Phase 13 → HR
Phase 14 → Automation Engine
Phase 15 → AI Everywhere
Phase 16 → Analytics
Phase 17 → Integrations
Phase 18 → Mobile / PWA
```

---

## How to Use This Repository

1. **Give your coding AI** the [Master Prompt](docs/AXORKS_OS_MASTER_PROMPT.md) once at the start of every session.
2. **Then give it** the specific phase prompt from [Phase Prompts](docs/phases/PHASE_PROMPTS.md).
3. **Reference** architecture docs when making technical decisions.

---

## License

Proprietary — Axorks. All rights reserved.
