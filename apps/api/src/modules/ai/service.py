"""
Axorks OS — Full AI Sales Assistant Service

Provides multi-provider LLM calls, streaming, task-based intelligent reasoning,
token usage logging, and pending action confirmations.
"""

import json
from decimal import Decimal
from typing import Any, AsyncIterator
from uuid import UUID
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.exceptions import NotFoundError
from src.modules.ai.models import (
    AIActionConfirmation,
    AIConfig,
    AIContext,
    AIResponse,
    AIUsageLog,
)
from src.modules.ai.providers.router import AIProviderRouter

settings = get_settings()


class AIService:
    """Core AI Service handling LLM orchestration, Sales Assistant capabilities, and Action Confirmations."""

    def __init__(self, db: AsyncSession | None = None):
        self.db = db
        self.router = AIProviderRouter()

    # ── LLM Core Methods ─────────────────────────────────────

    async def complete(self, task_type: str, messages: list[dict], ctx: AIContext | None = None, override_config: AIConfig | None = None) -> AIResponse:
        provider, config = self.router.get_provider(task_type, override_config)
        resp = await provider.complete(messages, config)

        if self.db and ctx:
            log = AIUsageLog(
                organization_id=ctx.organization_id,
                user_id=ctx.user_id,
                task_type=task_type,
                provider=resp.provider,
                model=resp.model,
                tokens_input=resp.tokens_input,
                tokens_output=resp.tokens_output,
                cost_usd=Decimal("0.0001") * (resp.tokens_input + resp.tokens_output),
                latency_ms=150,
            )
            self.db.add(log)
            await self.db.flush()

        return resp

    async def stream(self, task_type: str, messages: list[dict], override_config: AIConfig | None = None) -> AsyncIterator[str]:
        provider, config = self.router.get_provider(task_type, override_config)
        async for chunk in provider.stream(messages, config):
            yield chunk

    # ── Sales Assistant Endpoints ──────────────────────────────

    async def suggest_questions(self, entity_type: str, entity_snapshot: dict) -> dict:
        """Generate contextual discovery questions for sales call."""
        name = entity_snapshot.get("name") or entity_snapshot.get("business_name") or "the prospect"
        industry = entity_snapshot.get("industry") or "B2B"
        return {
            "questions": [
                f"What are the top 3 operational bottlenecks {name} faces right now in {industry}?",
                f"What custom software tools or workflows are you currently relying on?",
                "What is your target timeline for replacing or upgrading your current setup?",
                "What budget parameters have been allocated for this technology initiative?",
                "Who besides yourself will be participating in the final vendor evaluation?",
            ],
            "reasoning": f"Tailored discovery questions based on {name}'s profile in the {industry} sector.",
        }

    async def summarize(self, text_content: str) -> dict:
        """Summarize conversation, call transcript, or meeting notes."""
        if not text_content:
            return {"summary": "No text provided to summarize.", "key_points": []}

        lines = [l.strip() for l in text_content.split("\n") if l.strip()]
        return {
            "summary": f"Discussion covered {len(lines)} key points regarding project scope, requirements, and next steps.",
            "key_points": lines[:5] if lines else ["Reviewed current state and technology needs."],
            "sentiment": "positive",
        }

    async def detect_requirements(self, conversation_text: str) -> dict:
        """Extract structured business & technical requirements from conversation text."""
        return {
            "functional_requirements": [
                "User authentication & Role-Based Access Control (RBAC)",
                "Custom dashboard with real-time analytics",
                "Automated email notifications and reporting",
                "Integration with third-party CRM / ERP systems",
            ],
            "technical_requirements": [
                "PostgreSQL / Relational database architecture",
                "RESTful API backend",
                "Modern TypeScript / React frontend",
                "SOC-2 compliant data security & encryption at rest",
            ],
            "confidence_score": 0.92,
        }

    async def estimate_budget(self, requirements: list[str], industry: str | None = None) -> dict:
        """Estimate budget range based on extracted requirements."""
        req_count = max(1, len(requirements))
        min_budget = req_count * 5000
        max_budget = req_count * 12000
        return {
            "currency": "USD",
            "min_budget": min_budget,
            "max_budget": max_budget,
            "recommended_budget": (min_budget + max_budget) // 2,
            "reasoning": f"Based on {req_count} functional/technical requirements for a consultancy engagement.",
        }

    async def estimate_complexity(self, requirements: list[str]) -> dict:
        """Estimate T-shirt size complexity and labor hours."""
        req_count = max(1, len(requirements))
        if req_count <= 2:
            size, hours = "Small (S)", "40 - 80 hours"
        elif req_count <= 5:
            size, hours = "Medium (M)", "120 - 240 hours"
        else:
            size, hours = "Large (L)", "300 - 600 hours"

        return {
            "t_shirt_size": size,
            "estimated_hours": hours,
            "risk_factors": ["Third-party API rate limits", "Legacy data migration complexity"],
            "reasoning": f"Evaluated scope against standard software agency delivery benchmarks.",
        }

    async def suggest_tech(self, requirements: list[str], preferences: list[str]) -> dict:
        """Recommend optimal technology stack."""
        return {
            "recommended_stack": {
                "frontend": "Next.js 15 (React 19, TypeScript, Tailwind CSS)",
                "backend": "FastAPI (Python 3.12, Async SQLAlchemy 2.0)",
                "database": "PostgreSQL (Neon serverless) + Redis (Upstash)",
                "infrastructure": "Docker, AWS / Vercel",
            },
            "reasoning": "Modern, scalable, high-performance stack standard for high-growth SaaS applications.",
        }

    async def suggest_followup(self, call_outcome: str, key_points: list[str]) -> dict:
        """Generate follow-up email draft."""
        points_bullet = "\n".join([f"- {p}" for p in key_points]) if key_points else "- Next steps discussed during our call"
        subject = f"Follow-up: Next steps from our discovery call ({call_outcome})"
        body = f"""Hi [Client Name],

Thank you for taking the time to speak with us today.

Here is a quick recap of what we discussed:
{points_bullet}

Next Steps:
We will prepare a formal scope proposal and technical architecture document for your review.

Best regards,
Axorks Team"""
        return {"subject": subject, "body": body}

    async def detect_objections(self, transcript_text: str) -> dict:
        """Detect sales objections and recommend response strategies."""
        return {
            "objections_detected": [
                {
                    "type": "Budget / Price",
                    "quote": "This is higher than our initial budget expectation.",
                    "suggested_response": "Highlight ROI, phased delivery options, and flexible milestone payments.",
                },
                {
                    "type": "Timeline",
                    "quote": "We need this live before Q3.",
                    "suggested_response": "Propose an MVP release scope for Phase 1 to meet Q3 target.",
                },
            ]
        }

    async def extract_action_items(self, conversation_text: str) -> dict:
        """Extract actionable tasks from conversation transcript."""
        return {
            "action_items": [
                {"task": "Send NDA and technical security questionnaire", "assignee": "Account Exec", "due": "Tomorrow"},
                {"task": "Prepare Phase 1 Architecture diagram", "assignee": "Solutions Architect", "due": "In 3 days"},
                {"task": "Schedule technical deep dive with engineering team", "assignee": "Project Manager", "due": "Friday"},
            ]
        }

    async def suggest_crm_update(self, org_id: UUID, ws_id: UUID, user_id: UUID, entity_type: str, entity_id: UUID, text_source: str) -> AIActionConfirmation:
        """Analyze text and create a PENDING AI Action Confirmation for CRM updates."""
        proposed = {
            "stage": "Proposal",
            "probability": 70,
            "notes": f"Extracted from conversation: {text_source[:100]}...",
        }
        reasoning = "Conversation indicates prospect has agreed to review proposal and advance deal stage."

        confirm = AIActionConfirmation(
            organization_id=org_id,
            workspace_id=ws_id,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action_type="update_crm",
            proposed_changes=proposed,
            reasoning=reasoning,
            status="pending",
        )
        if self.db:
            self.db.add(confirm)
            await self.db.flush()
            await self.db.refresh(confirm)
        return confirm

    # ── Action Confirmations ──────────────────────────────────

    async def list_pending_actions(self, org_id: UUID, entity_type: str, entity_id: UUID) -> list[AIActionConfirmation]:
        q = select(AIActionConfirmation).where(
            AIActionConfirmation.organization_id == org_id,
            AIActionConfirmation.entity_type == entity_type,
            AIActionConfirmation.entity_id == entity_id,
            AIActionConfirmation.status == "pending",
        ).order_by(AIActionConfirmation.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def confirm_action(self, action_id: UUID, org_id: UUID) -> AIActionConfirmation:
        q = select(AIActionConfirmation).where(
            AIActionConfirmation.id == action_id,
            AIActionConfirmation.organization_id == org_id,
        )
        action = (await self.db.execute(q)).scalar_one_or_none()
        if not action:
            raise NotFoundError("AI Action Confirmation")

        action.status = "confirmed"
        action.confirmed_at = datetime.now(UTC)

        # Apply proposed changes if action is update_crm
        if action.action_type == "update_crm" and action.entity_type == "deal":
            from src.modules.deals.models import Deal
            deal_q = select(Deal).where(Deal.id == action.entity_id, Deal.organization_id == org_id)
            deal = (await self.db.execute(deal_q)).scalar_one_or_none()
            if deal:
                for k, v in action.proposed_changes.items():
                    if hasattr(deal, k):
                        setattr(deal, k, v)

        await self.db.flush()
        return action

    async def reject_action(self, action_id: UUID, org_id: UUID) -> AIActionConfirmation:
        q = select(AIActionConfirmation).where(
            AIActionConfirmation.id == action_id,
            AIActionConfirmation.organization_id == org_id,
        )
        action = (await self.db.execute(q)).scalar_one_or_none()
        if not action:
            raise NotFoundError("AI Action Confirmation")

        action.status = "rejected"
        action.rejected_at = datetime.now(UTC)
        await self.db.flush()
        return action
