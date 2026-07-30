# Axorks OS — Database Architecture

> PostgreSQL on Neon | SQLAlchemy 2.0 | Alembic Migrations

---

## 1. Design Goals

- Support **10M+ leads**, **100K+ companies**, **millions of activities**
- **Multi-tenant** isolation with `organization_id` on every business table
- **Soft deletes**, **audit logs**, **version history** on critical entities
- **Optimistic locking** via `version` column on concurrent-edit entities
- **Full-text search** via PostgreSQL `tsvector`
- **Event sourcing** for automation executions and financial audit trail

---

## 2. Naming Conventions

| Rule | Example |
|------|---------|
| Tables | snake_case, plural (`leads`, `invoice_items`) |
| Primary keys | `id` UUID v7 (time-sortable) |
| Foreign keys | `{entity}_id` |
| Timestamps | `created_at`, `updated_at`, `deleted_at` |
| Tenant columns | `organization_id`, `workspace_id` |
| Enums | PostgreSQL native enums or check constraints |

---

## 3. Core Schema — Foundation (Phase 1)

### organizations

```sql
CREATE TABLE organizations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    logo_url        TEXT,
    plan            VARCHAR(50) DEFAULT 'free',
    settings        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
```

### workspaces

```sql
CREATE TABLE workspaces (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) NOT NULL,
    is_default      BOOLEAN DEFAULT false,
    settings        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    UNIQUE (organization_id, slug)
);
CREATE INDEX idx_workspaces_org ON workspaces (organization_id) WHERE deleted_at IS NULL;
```

### users

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    email_verified  BOOLEAN DEFAULT false,
    password_hash   TEXT,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    avatar_url      TEXT,
    phone           VARCHAR(50),
    timezone        VARCHAR(50) DEFAULT 'UTC',
    locale          VARCHAR(10) DEFAULT 'en',
    preferences     JSONB DEFAULT '{}',
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret  TEXT,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
```

### organization_members

```sql
CREATE TABLE organization_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id         UUID NOT NULL REFERENCES users(id),
    role            VARCHAR(50) NOT NULL DEFAULT 'member',
    invited_by      UUID REFERENCES users(id),
    joined_at       TIMESTAMPTZ DEFAULT now(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, user_id)
);
CREATE INDEX idx_org_members_user ON organization_members (user_id);
```

### workspace_members

```sql
CREATE TABLE workspace_members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id),
    user_id         UUID NOT NULL REFERENCES users(id),
    role            VARCHAR(50) NOT NULL DEFAULT 'member',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (workspace_id, user_id)
);
```

### roles & permissions (RBAC)

```sql
CREATE TABLE roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    is_system       BOOLEAN DEFAULT false,
    permissions     JSONB NOT NULL DEFAULT '[]',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, name)
);

CREATE TABLE role_assignments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id         UUID NOT NULL REFERENCES roles(id),
    user_id         UUID NOT NULL REFERENCES users(id),
    scope_type      VARCHAR(20) NOT NULL, -- 'organization' | 'workspace'
    scope_id        UUID NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### audit_logs

```sql
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    user_id         UUID,
    action          VARCHAR(100) NOT NULL,
    entity_type     VARCHAR(100) NOT NULL,
    entity_id       UUID,
    old_values      JSONB,
    new_values      JSONB,
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_org_created ON audit_logs (organization_id, created_at DESC);
CREATE INDEX idx_audit_entity ON audit_logs (entity_type, entity_id);
```

### activity_logs (user-facing timeline)

```sql
CREATE TABLE activity_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID,
    entity_type     VARCHAR(100) NOT NULL,
    entity_id         UUID NOT NULL,
    actor_id          UUID REFERENCES users(id),
    action            VARCHAR(100) NOT NULL,
    metadata          JSONB DEFAULT '{}',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_activity_entity ON activity_logs (entity_type, entity_id, created_at DESC);
CREATE INDEX idx_activity_org ON activity_logs (organization_id, created_at DESC);
```

### notifications

```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    user_id         UUID NOT NULL REFERENCES users(id),
    type            VARCHAR(100) NOT NULL,
    title           VARCHAR(255) NOT NULL,
    body            TEXT,
    link            TEXT,
    read_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_notifications_user_unread ON notifications (user_id, created_at DESC) WHERE read_at IS NULL;
```

---

## 4. Lead Intelligence Schema (Phase 2)

### leads

```sql
CREATE TYPE lead_status AS ENUM (
    'new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost', 'archived'
);

CREATE TYPE lead_source AS ENUM (
    'linkedin', 'instagram', 'facebook', 'youtube', 'website',
    'cold_call', 'cold_email', 'referral', 'manual', 'csv', 'api',
    'google_business', 'directory', 'other'
);

CREATE TABLE leads (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id),
    workspace_id        UUID NOT NULL REFERENCES workspaces(id),
    
    -- Business info
    business_name       VARCHAR(500),
    website             TEXT,
    industry            VARCHAR(200),
    country             VARCHAR(100),
    company_size        VARCHAR(50),
    revenue_range       VARCHAR(50),
    linkedin_url        TEXT,
    
    -- Decision maker
    decision_maker_name VARCHAR(255),
    decision_maker_title VARCHAR(255),
    phone               VARCHAR(50),
    email               VARCHAR(255),
    
    -- CRM fields
    source              lead_source DEFAULT 'manual',
    source_detail       TEXT,
    status              lead_status DEFAULT 'new',
    score               INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    owner_id            UUID REFERENCES users(id),
    notes               TEXT,
    tags                TEXT[] DEFAULT '{}',
    custom_fields       JSONB DEFAULT '{}',
    
    -- Metadata
    version             INTEGER DEFAULT 1,
    search_vector       TSVECTOR,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

CREATE INDEX idx_leads_org_ws ON leads (organization_id, workspace_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_status ON leads (organization_id, status) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_owner ON leads (organization_id, owner_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_score ON leads (organization_id, score DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_leads_tags ON leads USING gin (tags);
CREATE INDEX idx_leads_search ON leads USING gin (search_vector);
CREATE INDEX idx_leads_created ON leads (organization_id, created_at DESC) WHERE deleted_at IS NULL;
```

### lead_scores_history

```sql
CREATE TABLE lead_score_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id         UUID NOT NULL REFERENCES leads(id),
    old_score       INTEGER,
    new_score       INTEGER NOT NULL,
    reason          TEXT,
    scored_by       VARCHAR(50), -- 'manual' | 'ai' | 'automation'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### lead_imports

```sql
CREATE TABLE lead_imports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    filename        VARCHAR(500),
    total_rows      INTEGER,
    imported_rows   INTEGER DEFAULT 0,
    failed_rows     INTEGER DEFAULT 0,
    status          VARCHAR(50) DEFAULT 'pending',
    error_log       JSONB,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 5. CRM Schema (Phase 3)

### companies

```sql
CREATE TABLE companies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    name            VARCHAR(500) NOT NULL,
    website         TEXT,
    industry        VARCHAR(200),
    country         VARCHAR(100),
    size            VARCHAR(50),
    revenue_range   VARCHAR(50),
    linkedin_url    TEXT,
    logo_url        TEXT,
    lead_id         UUID REFERENCES leads(id),
    owner_id        UUID REFERENCES users(id),
    tags            TEXT[] DEFAULT '{}',
    custom_fields   JSONB DEFAULT '{}',
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
```

### contacts

```sql
CREATE TABLE contacts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    company_id      UUID REFERENCES companies(id),
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    email           VARCHAR(255),
    phone           VARCHAR(50),
    title           VARCHAR(200),
    linkedin_url    TEXT,
    is_primary      BOOLEAN DEFAULT false,
    owner_id        UUID REFERENCES users(id),
    tags            TEXT[] DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
```

### deals

```sql
CREATE TABLE deals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    company_id      UUID REFERENCES companies(id),
    contact_id      UUID REFERENCES contacts(id),
    lead_id         UUID REFERENCES leads(id),
    title           VARCHAR(500) NOT NULL,
    value           DECIMAL(15,2),
    currency        VARCHAR(3) DEFAULT 'USD',
    status          VARCHAR(50) DEFAULT 'open',
    stage           VARCHAR(100),
    probability     INTEGER CHECK (probability >= 0 AND probability <= 100),
    expected_close  DATE,
    owner_id        UUID REFERENCES users(id),
    won_at          TIMESTAMPTZ,
    lost_at         TIMESTAMPTZ,
    lost_reason     TEXT,
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
```

### notes, calls, emails (polymorphic)

```sql
CREATE TABLE notes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    entity_type     VARCHAR(100) NOT NULL,
    entity_id         UUID NOT NULL,
    content           TEXT NOT NULL,
    is_pinned         BOOLEAN DEFAULT false,
    created_by        UUID REFERENCES users(id),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at        TIMESTAMPTZ
);
CREATE INDEX idx_notes_entity ON notes (entity_type, entity_id) WHERE deleted_at IS NULL;

CREATE TABLE calls (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    entity_type     VARCHAR(100) NOT NULL,
    entity_id         UUID NOT NULL,
    direction         VARCHAR(20), -- inbound | outbound
    duration_seconds  INTEGER,
    outcome           VARCHAR(100),
    recording_url     TEXT,
    transcript        TEXT,
    ai_summary        TEXT,
    called_at         TIMESTAMPTZ NOT NULL,
    created_by        UUID REFERENCES users(id),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE emails (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    entity_type     VARCHAR(100) NOT NULL,
    entity_id         UUID NOT NULL,
    direction         VARCHAR(20),
    subject           VARCHAR(500),
    body_html         TEXT,
    body_text         TEXT,
    from_address      VARCHAR(255),
    to_addresses      TEXT[],
    sent_at           TIMESTAMPTZ,
    external_id       VARCHAR(255),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### files (attachments)

```sql
CREATE TABLE files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID,
    entity_type     VARCHAR(100),
    entity_id         UUID,
    filename          VARCHAR(500) NOT NULL,
    mime_type         VARCHAR(100),
    size_bytes        BIGINT,
    storage_provider  VARCHAR(50) DEFAULT 'cloudinary',
    storage_key       TEXT NOT NULL,
    url               TEXT,
    uploaded_by       UUID REFERENCES users(id),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at        TIMESTAMPTZ
);
```

---

## 6. Proposals Schema (Phase 5)

```sql
CREATE TABLE proposals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    deal_id         UUID REFERENCES deals(id),
    company_id      UUID REFERENCES companies(id),
    title           VARCHAR(500) NOT NULL,
    type            VARCHAR(50), -- proposal | quotation | sow | contract
    status          VARCHAR(50) DEFAULT 'draft',
    content         JSONB NOT NULL DEFAULT '{}',
    total_value     DECIMAL(15,2),
    currency        VARCHAR(3) DEFAULT 'USD',
    valid_until     DATE,
    sent_at         TIMESTAMPTZ,
    accepted_at     TIMESTAMPTZ,
    pdf_url         TEXT,
    version         INTEGER DEFAULT 1,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE TABLE proposal_milestones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id     UUID NOT NULL REFERENCES proposals(id),
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    amount          DECIMAL(15,2),
    due_date        DATE,
    sort_order      INTEGER DEFAULT 0
);
```

---

## 7. Projects Schema (Phase 6)

```sql
CREATE TABLE projects (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    company_id      UUID REFERENCES companies(id),
    deal_id         UUID REFERENCES deals(id),
    proposal_id     UUID REFERENCES proposals(id),
    name            VARCHAR(500) NOT NULL,
    description     TEXT,
    status          VARCHAR(50) DEFAULT 'planning',
    start_date      DATE,
    end_date        DATE,
    budget          DECIMAL(15,2),
    currency        VARCHAR(3) DEFAULT 'USD',
    owner_id        UUID REFERENCES users(id),
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE TABLE sprints (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(id),
    name            VARCHAR(255) NOT NULL,
    goal            TEXT,
    start_date      DATE,
    end_date        DATE,
    status          VARCHAR(50) DEFAULT 'planned'
);

CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    project_id      UUID REFERENCES projects(id),
    sprint_id       UUID REFERENCES sprints(id),
    parent_id       UUID REFERENCES tasks(id),
    epic_id         UUID,
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    type            VARCHAR(50) DEFAULT 'task', -- epic | story | task | subtask | bug
    status          VARCHAR(50) DEFAULT 'backlog',
    priority        VARCHAR(20) DEFAULT 'medium',
    assignee_id     UUID REFERENCES users(id),
    due_date        DATE,
    estimate_hours  DECIMAL(8,2),
    sort_order      INTEGER DEFAULT 0,
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_tasks_project ON tasks (project_id, status) WHERE deleted_at IS NULL;

CREATE TABLE time_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    task_id         UUID REFERENCES tasks(id),
    project_id      UUID REFERENCES projects(id),
    user_id         UUID NOT NULL REFERENCES users(id),
    hours           DECIMAL(8,2) NOT NULL,
    description     TEXT,
    logged_date     DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 8. Finance Schema (Phase 9)

```sql
CREATE TABLE invoices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    company_id      UUID REFERENCES companies(id),
    project_id      UUID REFERENCES projects(id),
    proposal_id     UUID REFERENCES proposals(id),
    invoice_number  VARCHAR(50) NOT NULL,
    status          VARCHAR(50) DEFAULT 'draft',
    issue_date      DATE,
    due_date        DATE,
    subtotal        DECIMAL(15,2),
    tax_amount      DECIMAL(15,2),
    total           DECIMAL(15,2),
    currency        VARCHAR(3) DEFAULT 'USD',
    notes           TEXT,
    pdf_url         TEXT,
    paid_at         TIMESTAMPTZ,
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    UNIQUE (organization_id, invoice_number)
);

CREATE TABLE invoice_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id      UUID NOT NULL REFERENCES invoices(id),
    description     TEXT NOT NULL,
    quantity        DECIMAL(10,2) DEFAULT 1,
    unit_price      DECIMAL(15,2) NOT NULL,
    amount          DECIMAL(15,2) NOT NULL,
    sort_order      INTEGER DEFAULT 0
);

CREATE TABLE expenses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    project_id      UUID REFERENCES projects(id),
    category        VARCHAR(100),
    description     TEXT,
    amount          DECIMAL(15,2) NOT NULL,
    currency        VARCHAR(3) DEFAULT 'USD',
    expense_date    DATE NOT NULL,
    receipt_url     TEXT,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 9. AI Schema (Phase 4, 15)

```sql
CREATE TABLE ai_conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID NOT NULL,
    entity_type     VARCHAR(100),
    entity_id         UUID,
    user_id         UUID NOT NULL REFERENCES users(id),
    context_type    VARCHAR(100), -- sales_call | proposal | email | general
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ai_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES ai_conversations(id),
    role            VARCHAR(20) NOT NULL, -- user | assistant | system
    content         TEXT NOT NULL,
    model           VARCHAR(100),
    tokens_used     INTEGER,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ai_suggestions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    entity_type     VARCHAR(100) NOT NULL,
    entity_id         UUID NOT NULL,
    suggestion_type VARCHAR(100) NOT NULL,
    content         JSONB NOT NULL,
    confidence      DECIMAL(5,4),
    status          VARCHAR(50) DEFAULT 'pending', -- pending | accepted | rejected
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ai_action_confirmations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    user_id         UUID NOT NULL,
    action_type     VARCHAR(100) NOT NULL,
    action_payload  JSONB NOT NULL,
    status          VARCHAR(50) DEFAULT 'pending',
    confirmed_at    TIMESTAMPTZ,
    executed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 10. Automation Schema (Phase 14)

```sql
CREATE TABLE workflows (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    workspace_id    UUID,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    trigger_type    VARCHAR(100) NOT NULL,
    trigger_config  JSONB NOT NULL DEFAULT '{}',
    is_active       BOOLEAN DEFAULT true,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE workflow_steps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id     UUID NOT NULL REFERENCES workflows(id),
    step_type       VARCHAR(50) NOT NULL, -- condition | action
    config          JSONB NOT NULL DEFAULT '{}',
    sort_order      INTEGER NOT NULL,
    parent_step_id  UUID REFERENCES workflow_steps(id)
);

CREATE TABLE workflow_executions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id     UUID NOT NULL REFERENCES workflows(id),
    trigger_event   JSONB NOT NULL,
    status          VARCHAR(50) DEFAULT 'running',
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    error           TEXT,
    steps_log       JSONB DEFAULT '[]'
);
CREATE INDEX idx_workflow_exec ON workflow_executions (workflow_id, started_at DESC);
```

---

## 11. Version History Pattern

For entities requiring version history (proposals, contracts, SOWs):

```sql
CREATE TABLE entity_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    entity_type     VARCHAR(100) NOT NULL,
    entity_id         UUID NOT NULL,
    version_number    INTEGER NOT NULL,
    snapshot          JSONB NOT NULL,
    changed_by        UUID REFERENCES users(id),
    change_summary    TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (entity_type, entity_id, version_number)
);
```

---

## 12. Optimistic Locking

All concurrent-edit entities include:

```sql
version INTEGER DEFAULT 1 NOT NULL
```

Update pattern:

```sql
UPDATE leads SET ..., version = version + 1
WHERE id = :id AND version = :expected_version;
-- If 0 rows affected → 409 Conflict
```

---

## 13. Search Vector Maintenance

```sql
CREATE OR REPLACE FUNCTION leads_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.business_name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.decision_maker_name, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(NEW.email, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(NEW.notes, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER leads_search_update
    BEFORE INSERT OR UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION leads_search_vector_update();
```

---

## 14. Partitioning Strategy (10M+ Scale)

```sql
-- Partition activity_logs by month
CREATE TABLE activity_logs (
    ...
) PARTITION BY RANGE (created_at);

-- Partition leads by organization_id hash (when single org exceeds 1M)
-- Or list partition for largest tenants
```

---

## 15. Migration Strategy

1. All schema changes via **Alembic** migrations
2. Migrations are **forward-only** in production
3. Destructive changes require multi-step migrations (add → migrate → drop)
4. Seed data for system roles and default workspace templates
5. PR preview databases via Neon branches

---

*Reference this document when implementing any database module.*
