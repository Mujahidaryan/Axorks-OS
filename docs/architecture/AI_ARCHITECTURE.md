# Axorks OS — AI Architecture

> AI as Infrastructure, Not a Feature

---

## 1. Design Principles

| Principle | Rule |
|-----------|------|
| **Observe, don't interrupt** | AI suggestions appear inline, never block workflow |
| **Assist, don't replace** | Human makes all decisions; AI recommends |
| **Explain recommendations** | Every suggestion includes reasoning |
| **Never hallucinate business data** | AI cannot invent CRM records, amounts, or dates |
| **Confirm destructive actions** | Updates to CRM, sends, deletes require explicit approval |
| **Not a separate page** | AI exists on every screen via contextual panels and inline actions |

---

## 2. Provider Abstraction Layer

```
┌─────────────────────────────────────────────────┐
│              AI Service (apps/api)               │
│                                                  │
│  AIService.complete(prompt, config) → Response   │
│  AIService.stream(prompt, config) → AsyncIterator│
│  AIService.embed(text) → Vector                  │
│  AIService.classify(text, labels) → Label        │
└────────────────────┬────────────────────────────┘
                     │
         ┌───────────┼───────────┬───────────┐
         ▼           ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ OpenAI  │ │Anthropic│ │ Gemini  │ │DeepSeek │
    │ GPT-4o  │ │ Claude  │ │  Pro    │ │  Chat   │
    └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### Interface Definition

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class AIConfig(BaseModel):
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    provider: str | None = None  # auto-select if None

class AIResponse(BaseModel):
    content: str
    model: str
    provider: str
    tokens_input: int
    tokens_output: int
    finish_reason: str

class AIProvider(ABC):
    name: str

    @abstractmethod
    async def complete(self, messages: list[dict], config: AIConfig) -> AIResponse: ...

    @abstractmethod
    async def stream(self, messages: list[dict], config: AIConfig) -> AsyncIterator[str]: ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...
```

### Provider Router

```python
class AIProviderRouter:
    """Route tasks to optimal provider based on config and task type."""

    TASK_DEFAULTS = {
        "sales_assistant": {"provider": "anthropic", "model": "claude-sonnet-4"},
        "proposal_generate": {"provider": "openai", "model": "gpt-4o"},
        "classify_lead": {"provider": "openai", "model": "gpt-4o-mini"},
        "summarize_call": {"provider": "anthropic", "model": "claude-haiku"},
        "embed_search": {"provider": "openai", "model": "text-embedding-3-small"},
    }

    def get_provider(self, task_type: str, override: AIConfig | None = None) -> AIProvider:
        defaults = self.TASK_DEFAULTS.get(task_type, {})
        provider_name = (override and override.provider) or defaults.get("provider", "openai")
        return self.providers[provider_name]
```

---

## 3. AI Context System

Every AI call receives structured context:

```python
class AIContext(BaseModel):
    organization_id: UUID
    workspace_id: UUID
    user_id: UUID
    entity_type: str | None = None      # lead, deal, project, etc.
    entity_id: UUID | None = None
    entity_snapshot: dict | None = None  # Relevant CRM data (never full DB)
    conversation_history: list[dict] = []
    task_type: str                        # sales_assistant, summarize, generate, etc.
```

### Context Builder

```python
class AIContextBuilder:
    async def build(self, ctx: TenantContext, entity_type: str, entity_id: UUID) -> AIContext:
        """Fetch only relevant fields for the entity — never dump entire records."""
        snapshot = await self.repo.get_ai_snapshot(entity_type, entity_id, ctx)
        return AIContext(
            organization_id=ctx.organization_id,
            workspace_id=ctx.workspace_id,
            user_id=ctx.user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_snapshot=snapshot,
        )
```

---

## 4. AI Features by Phase

### Phase 4 — AI Sales Assistant

| Feature | Trigger | Output |
|---------|---------|--------|
| Question suggestions | During call/meeting | Inline suggestion chips |
| Live summary | End of call | Summary card → confirm to save |
| Requirement detection | Conversation transcript | Extracted requirements list |
| Budget estimation | Requirements + industry | Range estimate with reasoning |
| Complexity estimation | Requirements | T-shirt size + hour range |
| Tech stack suggestion | Requirements | Recommended technologies |
| Follow-up suggestion | Call outcome | Email/message draft |
| Proposal suggestion | Qualified lead | Trigger proposal workflow |
| Objection detection | Live transcript | Objection + suggested response |
| Action items | Any conversation | Task list → confirm to create |
| CRM auto-update | Confirmed actions | Update lead/deal fields |

### Phase 5 — Proposal Generator

| Feature | Input | Output |
|---------|-------|--------|
| Full proposal | Lead + requirements + templates | Structured proposal document |
| Quotation | Scope + rates | Line-item quotation |
| SOW | Project scope | Statement of Work |
| Architecture doc | Technical requirements | Architecture document |
| Timeline | Scope + team size | Gantt-ready milestones |
| Payment plan | Total value + preferences | Milestone payment schedule |
| PDF/Word export | Generated content | Formatted documents |

### Phase 15 — AI Everywhere

Every screen gets contextual AI actions:

| Screen | AI Actions |
|--------|------------|
| Lead detail | Score explanation, enrich, draft email, suggest next step |
| CRM record | Summarize relationship, predict close date, suggest upsell |
| Project board | Sprint summary, risk detection, standup generator |
| Invoice | Payment reminder draft, anomaly detection |
| Knowledge base | Improve writing, translate, generate from outline |
| Email compose | Rewrite, shorten, translate, tone adjust |
| Any text field | Summarize, improve, expand, translate |
| Search | Natural language query → structured filter |
| Dashboard | Narrative insights, anomaly alerts, forecasts |

---

## 5. Prompt Management

### Prompt Library (Database)

```sql
CREATE TABLE ai_prompts (
    id              UUID PRIMARY KEY,
    organization_id UUID,           -- NULL = system prompt
    name            VARCHAR(255) NOT NULL,
    task_type       VARCHAR(100) NOT NULL,
    system_prompt   TEXT NOT NULL,
    user_template   TEXT,           -- Jinja2 template
    variables       JSONB DEFAULT '[]',
    model_config    JSONB DEFAULT '{}',
    version         INTEGER DEFAULT 1,
    is_active       BOOLEAN DEFAULT true
);
```

### Prompt Rendering

```python
class PromptRenderer:
    def render(self, prompt: AIPrompt, context: AIContext) -> list[dict]:
        system = prompt.system_prompt
        user = Template(prompt.user_template).render(
            entity=context.entity_snapshot,
            user=context.user_snapshot,
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
```

---

## 6. Streaming Architecture

```
Frontend                    Backend                     AI Provider
   │                           │                            │
   │── POST /ai/stream ───────►│                            │
   │                           │── Build context ──────────►│
   │                           │── Render prompt ──────────►│
   │◄── SSE: token ────────────│◄── Stream tokens ──────────│
   │◄── SSE: token ────────────│◄── Stream tokens ──────────│
   │◄── SSE: done ─────────────│◄── Finish ─────────────────│
   │                           │── Log usage ────────────────►│ DB
```

Frontend uses `EventSource` or `fetch` with readable stream for SSE.

---

## 7. Action Confirmation Flow

```
AI suggests: "Update lead status to Qualified and assign to John"
    ↓
Frontend shows confirmation card with diff preview
    ↓
User clicks "Confirm" → POST /ai/actions/{id}/confirm
    ↓
Backend executes action → audit log → activity log → CRM update
    ↓
Frontend refreshes entity via TanStack Query invalidation
```

### Never Auto-Execute

- CRM field updates
- Email sends
- Task creation (batch > 1)
- Status changes
- File deletions
- Financial record changes

### Safe Auto-Execute (with logging)

- Text summarization (display only)
- Suggestion generation (display only)
- Search query interpretation
- Inline autocomplete

---

## 8. Token Usage & Cost Tracking

```sql
CREATE TABLE ai_usage_logs (
    id              UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    user_id         UUID NOT NULL,
    task_type       VARCHAR(100),
    provider        VARCHAR(50),
    model           VARCHAR(100),
    tokens_input    INTEGER,
    tokens_output   INTEGER,
    cost_usd        DECIMAL(10,6),
    latency_ms      INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Future: Usage-based billing per organization plan.

---

## 9. Frontend AI Components

```
packages/ui/src/ai/
├── AIInlineActions.tsx      # Summarize | Improve | Translate buttons
├── AISuggestionPanel.tsx    # Side panel for contextual suggestions
├── AIConfirmationCard.tsx   # Approve/reject AI-proposed actions
├── AIStreamingText.tsx      # Streaming response display
├── AIComposerAssist.tsx     # Email/message compose helper
└── AICommandPalette.tsx     # Natural language commands via Cmd+K
```

### UX Pattern

AI actions appear as subtle icon buttons near relevant content — never modal dialogs unless confirmation is needed.

---

## 10. Error Handling

| Scenario | Behavior |
|----------|----------|
| Provider down | Fallback to next provider in config |
| Rate limited | Queue request, show "AI busy" with retry |
| Context too large | Truncate intelligently, warn user |
| Unsafe output detected | Block display, log incident |
| Timeout (>30s) | Cancel, offer retry with smaller context |

---

*AI is the connective tissue of Axorks OS — not a bolt-on feature.*
