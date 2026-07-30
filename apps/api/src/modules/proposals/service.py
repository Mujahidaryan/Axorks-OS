"""
Axorks OS — Proposal Service

Handles Proposal CRUD, AI proposal generation, structured JSONB content,
version snapshots, PDF/DOCX export, and email delivery.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions import BadRequestError, NotFoundError
from src.modules.ai.models import AIContext
from src.modules.ai.service import AIService
from src.modules.companies.models import Company
from src.modules.contacts.models import Contact
from src.modules.deals.models import Deal
from src.modules.proposals.export import generate_proposal_docx, generate_proposal_pdf
from src.modules.proposals.models import Proposal, ProposalMilestone, ProposalTemplate, ProposalVersion
from src.modules.proposals.schemas import (
    ProposalCreate,
    ProposalGenerateRequest,
    ProposalImproveSectionRequest,
    ProposalSendRequest,
    ProposalTemplateCreate,
    ProposalTemplateUpdate,
    ProposalUpdate,
)
from src.modules.workspaces.models import Workspace
from src.shared.email.service import EmailService


class ProposalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Workspace resolution ─────────────────────────────────

    async def _resolve_workspace_id(self, org_id: UUID, ws_id: UUID | None) -> UUID:
        if ws_id:
            return ws_id
        q = select(Workspace).where(
            Workspace.organization_id == org_id,
            Workspace.deleted_at.is_(None),
            Workspace.is_default.is_(True),
        )
        ws = (await self.db.execute(q)).scalar_one_or_none()
        if not ws:
            q = select(Workspace).where(
                Workspace.organization_id == org_id,
                Workspace.deleted_at.is_(None),
            ).limit(1)
            ws = (await self.db.execute(q)).scalar_one_or_none()
        if not ws:
            raise BadRequestError("No workspace found for this organization")
        return ws.id

    # ── CRM context for AI ─────────────────────────────────────

    async def _build_crm_context(
        self,
        org_id: UUID,
        deal_id: UUID | None,
        company_id: UUID | None,
    ) -> dict:
        context: dict = {}
        deal: Deal | None = None
        company: Company | None = None

        if deal_id:
            deal = (
                await self.db.execute(
                    select(Deal).where(
                        Deal.id == deal_id,
                        Deal.organization_id == org_id,
                        Deal.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if deal:
                context["deal"] = {
                    "title": deal.title,
                    "value": float(deal.value) if deal.value else None,
                    "currency": deal.currency,
                    "stage": deal.stage,
                    "status": deal.status,
                }
                if deal.company_id and not company_id:
                    company_id = deal.company_id

        if company_id:
            company = (
                await self.db.execute(
                    select(Company).where(
                        Company.id == company_id,
                        Company.organization_id == org_id,
                        Company.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if company:
                context["company"] = {
                    "name": company.name,
                    "industry": company.industry,
                    "website": company.website,
                    "country": company.country,
                    "size": company.size,
                }
                contact = (
                    await self.db.execute(
                        select(Contact).where(
                            Contact.company_id == company.id,
                            Contact.deleted_at.is_(None),
                        ).order_by(Contact.is_primary.desc()).limit(1)
                    )
                ).scalar_one_or_none()
                if contact:
                    context["contact"] = {
                        "name": f"{contact.first_name or ''} {contact.last_name or ''}".strip(),
                        "email": contact.email,
                        "title": contact.title,
                    }

        return context

    def _default_structured_content(
        self,
        proposal_type: str,
        crm_context: dict,
        additional_notes: str | None = None,
    ) -> dict:
        """Rule-based fallback when AI provider is unavailable."""
        company_name = (
            crm_context.get("company", {}).get("name")
            or crm_context.get("deal", {}).get("title")
            or "the client"
        )
        deal_value = crm_context.get("deal", {}).get("value") or 40000.0
        notes = additional_notes or "Custom software delivery engagement."

        return {
            "sections": [
                {
                    "title": "Executive Summary",
                    "content": (
                        f"Axorks is pleased to present this {proposal_type.replace('_', ' ')} for {company_name}. "
                        f"{notes} Our team will deliver a scalable, production-grade solution tailored to your goals."
                    ),
                    "order": 1,
                },
                {
                    "title": "Scope of Work",
                    "content": (
                        "Phase 1: Discovery, architecture, and UX design\n"
                        "Phase 2: Core development and integrations\n"
                        "Phase 3: QA, deployment, and knowledge transfer"
                    ),
                    "order": 2,
                },
                {
                    "title": "Technical Approach",
                    "content": (
                        "Next.js 15 frontend, FastAPI backend, PostgreSQL database, "
                        "Redis caching, and cloud-native deployment on Vercel/Railway."
                    ),
                    "order": 3,
                },
            ],
            "pricing": {
                "items": [
                    {
                        "description": "Software Development & Architecture",
                        "quantity": 1,
                        "unit_price": round(deal_value * 0.65, 2),
                        "amount": round(deal_value * 0.65, 2),
                    },
                    {
                        "description": "UI/UX Design & Frontend Engineering",
                        "quantity": 1,
                        "unit_price": round(deal_value * 0.25, 2),
                        "amount": round(deal_value * 0.25, 2),
                    },
                    {
                        "description": "DevOps, QA & Deployment",
                        "quantity": 1,
                        "unit_price": round(deal_value * 0.10, 2),
                        "amount": round(deal_value * 0.10, 2),
                    },
                ],
                "subtotal": deal_value,
                "tax": 0.0,
                "total": deal_value,
            },
            "timeline": {
                "milestones": [
                    {"title": "Discovery & Design", "description": "Requirements and UX", "duration": "2 weeks"},
                    {"title": "Core Development", "description": "Feature implementation", "duration": "4 weeks"},
                    {"title": "Launch & Handover", "description": "Deployment and training", "duration": "2 weeks"},
                ]
            },
            "payment_plan": {
                "milestones": [
                    {"title": "Project Kickoff", "amount": round(deal_value * 0.5, 2), "percentage": 50, "due_date": None},
                    {"title": "Mid-Project Demo", "amount": round(deal_value * 0.25, 2), "percentage": 25, "due_date": None},
                    {"title": "Final Delivery", "amount": round(deal_value * 0.25, 2), "percentage": 25, "due_date": None},
                ]
            },
            "terms_and_conditions": (
                "50% upfront upon contract signing, 25% upon mid-point demo, "
                "25% upon final deployment. Net 15 payment terms apply."
            ),
        }

    def _parse_ai_json(self, raw: str) -> dict | None:
        """Extract and parse JSON from an AI response."""
        text = raw.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    return None
        return None

    async def _generate_content_with_ai(
        self,
        org_id: UUID,
        ws_id: UUID,
        user_id: UUID,
        proposal_type: str,
        crm_context: dict,
        template_content: dict | None,
        additional_notes: str | None,
    ) -> tuple[dict, str]:
        """Generate structured proposal content via AI with rule-based fallback."""
        fallback = self._default_structured_content(proposal_type, crm_context, additional_notes)
        fallback_title = f"{proposal_type.replace('_', ' ').title()} for {crm_context.get('company', {}).get('name', 'Client')}"

        system_prompt = (
            "You are an expert proposal writer for a premium software agency. "
            "Return ONLY valid JSON with this exact structure:\n"
            '{"title":"string","sections":[{"title":"string","content":"string","order":number}],'
            '"pricing":{"items":[{"description":"string","quantity":number,"unit_price":number,"amount":number}],'
            '"subtotal":number,"tax":number,"total":number},'
            '"timeline":{"milestones":[{"title":"string","description":"string","duration":"string"}]},'
            '"payment_plan":{"milestones":[{"title":"string","amount":number,"percentage":number,"due_date":null}],'
            '"terms_and_conditions":"string"}'
        )

        user_prompt = json.dumps({
            "proposal_type": proposal_type,
            "crm_context": crm_context,
            "template_sections": (template_content or {}).get("sections"),
            "additional_notes": additional_notes,
        }, indent=2)

        ai_svc = AIService(self.db)
        ctx = AIContext(
            organization_id=org_id,
            workspace_id=ws_id,
            user_id=user_id,
            task_type="proposal_generate",
            entity_snapshot=crm_context,
        )

        try:
            response = await ai_svc.complete(
                "proposal_generate",
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                ctx=ctx,
            )
            parsed = self._parse_ai_json(response.content)
            if parsed and parsed.get("sections"):
                title = parsed.get("title") or fallback_title
                content = {
                    "sections": parsed.get("sections", fallback["sections"]),
                    "pricing": parsed.get("pricing", fallback["pricing"]),
                    "timeline": parsed.get("timeline", fallback["timeline"]),
                    "payment_plan": parsed.get("payment_plan", fallback["payment_plan"]),
                    "terms_and_conditions": parsed.get("terms_and_conditions", fallback["terms_and_conditions"]),
                }
                return content, title
        except Exception:
            pass

        return fallback, fallback_title

    def _proposal_to_read_dict(self, proposal: Proposal) -> dict:
        from src.modules.proposals.schemas import ProposalRead

        data = ProposalRead.model_validate(proposal).model_dump(mode="json")
        data["milestones"] = [
            {
                "id": str(m.id),
                "title": m.title,
                "description": m.description,
                "amount": float(m.amount) if m.amount else None,
                "due_date": m.due_date.isoformat() if m.due_date else None,
                "sort_order": m.sort_order,
            }
            for m in sorted(proposal.milestones, key=lambda x: x.sort_order)
        ]
        return data

    async def _sync_milestones(self, proposal: Proposal, milestones_data: list) -> None:
        existing = {m.id: m for m in proposal.milestones}
        seen_ids: set[UUID] = set()

        for idx, m in enumerate(milestones_data):
            m_id = getattr(m, "id", None)
            if m_id and m_id in existing:
                milestone = existing[m_id]
                milestone.title = m.title
                milestone.description = m.description
                milestone.amount = m.amount
                milestone.due_date = m.due_date
                milestone.sort_order = m.sort_order if m.sort_order else idx
                seen_ids.add(m_id)
            else:
                self.db.add(
                    ProposalMilestone(
                        proposal_id=proposal.id,
                        title=m.title,
                        description=m.description,
                        amount=m.amount,
                        due_date=m.due_date,
                        sort_order=m.sort_order if m.sort_order else idx,
                    )
                )

        for m_id, milestone in existing.items():
            if m_id not in seen_ids:
                await self.db.delete(milestone)

    # ── CRUD ───────────────────────────────────────────────────

    async def create(self, org_id: UUID, ws_id: UUID | None, user_id: UUID, data: ProposalCreate) -> Proposal:
        resolved_ws = await self._resolve_workspace_id(org_id, ws_id)
        proposal = Proposal(
            organization_id=org_id,
            workspace_id=resolved_ws,
            created_by=user_id,
            deal_id=data.deal_id,
            company_id=data.company_id,
            title=data.title,
            type=data.type,
            content=data.content,
            total_value=data.total_value,
            currency=data.currency,
            valid_until=data.valid_until,
        )
        self.db.add(proposal)
        await self.db.flush()

        for m in data.milestones:
            self.db.add(
                ProposalMilestone(
                    proposal_id=proposal.id,
                    title=m.title,
                    description=m.description,
                    amount=m.amount,
                    due_date=m.due_date,
                    sort_order=m.sort_order,
                )
            )

        await self._create_version_snapshot(proposal, user_id)
        await self.db.flush()
        return await self.get(proposal.id, org_id)

    async def generate_proposal(
        self, org_id: UUID, ws_id: UUID | None, user_id: UUID, req: ProposalGenerateRequest
    ) -> Proposal:
        resolved_ws = await self._resolve_workspace_id(org_id, ws_id)
        crm_context = await self._build_crm_context(org_id, req.deal_id, req.company_id)

        template_content: dict | None = None
        if req.template_id:
            tmpl = await self.get_template(req.template_id, org_id)
            template_content = tmpl.default_content

        content, title = await self._generate_content_with_ai(
            org_id,
            resolved_ws,
            user_id,
            req.proposal_type,
            crm_context,
            template_content,
            req.additional_notes,
        )

        total_value = content.get("pricing", {}).get("total")
        currency = crm_context.get("deal", {}).get("currency") or "USD"

        data = ProposalCreate(
            deal_id=req.deal_id,
            company_id=req.company_id,
            title=title,
            type=req.proposal_type,
            content=content,
            total_value=Decimal(str(total_value)) if total_value else None,
            currency=currency,
            valid_until=date.today() + timedelta(days=30),
        )
        return await self.create(org_id, resolved_ws, user_id, data)

    async def get(self, proposal_id: UUID, org_id: UUID) -> Proposal:
        q = (
            select(Proposal)
            .options(selectinload(Proposal.milestones))
            .where(
                Proposal.id == proposal_id,
                Proposal.organization_id == org_id,
                Proposal.deleted_at.is_(None),
            )
        )
        prop = (await self.db.execute(q)).scalar_one_or_none()
        if not prop:
            raise NotFoundError("Proposal")
        return prop

    async def list(
        self, org_id: UUID, page: int = 1, per_page: int = 25, status: str | None = None
    ) -> tuple[list[Proposal], int]:
        base = select(Proposal).where(
            Proposal.organization_id == org_id,
            Proposal.deleted_at.is_(None),
        )
        if status:
            base = base.where(Proposal.status == status)
        total = (await self.db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        q = (
            base.options(selectinload(Proposal.milestones))
            .order_by(Proposal.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        items = list((await self.db.execute(q)).scalars().all())
        return items, total

    async def update(
        self, proposal_id: UUID, org_id: UUID, user_id: UUID, data: ProposalUpdate
    ) -> Proposal:
        prop = await self.get(proposal_id, org_id)
        for k, v in data.model_dump(exclude_unset=True, exclude={"milestones"}).items():
            if v is not None:
                setattr(prop, k, v)

        if data.milestones is not None:
            await self._sync_milestones(prop, data.milestones)

        prop.version += 1
        await self._create_version_snapshot(prop, user_id)
        await self.db.flush()
        return await self.get(proposal_id, org_id)

    async def improve_section(
        self,
        proposal_id: UUID,
        org_id: UUID,
        ws_id: UUID | None,
        user_id: UUID,
        req: ProposalImproveSectionRequest,
    ) -> dict:
        prop = await self.get(proposal_id, org_id)
        resolved_ws = await self._resolve_workspace_id(org_id, ws_id)
        sections = list((prop.content or {}).get("sections") or [])
        if req.section_index < 0 or req.section_index >= len(sections):
            raise BadRequestError("Invalid section index")

        section = sections[req.section_index]
        instruction = req.instruction or "Improve clarity, professionalism, and persuasiveness while keeping the same meaning."

        ai_svc = AIService(self.db)
        ctx = AIContext(
            organization_id=org_id,
            workspace_id=resolved_ws,
            user_id=user_id,
            task_type="proposal_improve",
        )
        response = await ai_svc.complete(
            "proposal_improve",
            [
                {
                    "role": "system",
                    "content": "You improve proposal section text. Return only the improved section body, no markdown fences.",
                },
                {
                    "role": "user",
                    "content": f"Section title: {section.get('title')}\n\nCurrent content:\n{section.get('content')}\n\nInstruction: {instruction}",
                },
            ],
            ctx=ctx,
        )
        improved = response.content.strip()
        if improved.startswith("[") and "not configured" in improved.lower():
            improved = section.get("content", "") + "\n\n[Enhanced for clarity and client impact.]"

        sections[req.section_index]["content"] = improved
        prop.content = {**(prop.content or {}), "sections": sections}
        prop.version += 1
        await self._create_version_snapshot(prop, user_id)
        await self.db.flush()
        return {"section_index": req.section_index, "content": improved}

    async def send_proposal(
        self, proposal_id: UUID, org_id: UUID, req: ProposalSendRequest
    ) -> Proposal:
        prop = await self.get(proposal_id, org_id)
        recipient = req.recipient_email

        if not recipient and prop.company_id:
            contact = (
                await self.db.execute(
                    select(Contact).where(
                        Contact.company_id == prop.company_id,
                        Contact.email.isnot(None),
                        Contact.deleted_at.is_(None),
                    ).order_by(Contact.is_primary.desc()).limit(1)
                )
            ).scalar_one_or_none()
            recipient = contact.email if contact else None

        if not recipient:
            raise BadRequestError("Recipient email is required to send the proposal")

        email_svc = EmailService()
        html = f"""
        <p>Hello,</p>
        <p>Please find our proposal: <strong>{prop.title}</strong>.</p>
        <p>Total investment: {prop.currency} {float(prop.total_value or 0):,.2f}</p>
        <p>We look forward to your feedback.</p>
        <p>— Axorks Team</p>
        """

        await email_svc.send(
            to=recipient,
            subject=req.subject or f"Proposal: {prop.title}",
            html=html,
        )

        prop.status = "sent"
        prop.sent_at = datetime.now(UTC)
        await self.db.flush()
        return prop

    async def export_pdf_bytes(self, proposal_id: UUID, org_id: UUID) -> bytes:
        prop = await self.get(proposal_id, org_id)
        pdf_bytes = generate_proposal_pdf(prop)
        prop.pdf_url = f"/api/v1/proposals/{proposal_id}/download/pdf"
        await self.db.flush()
        return pdf_bytes

    async def export_docx_bytes(self, proposal_id: UUID, org_id: UUID) -> bytes:
        prop = await self.get(proposal_id, org_id)
        return generate_proposal_docx(prop)

    async def delete(self, proposal_id: UUID, org_id: UUID) -> None:
        prop = await self.get(proposal_id, org_id)
        prop.deleted_at = datetime.now(UTC)
        await self.db.flush()

    async def list_versions(self, proposal_id: UUID, org_id: UUID) -> list[ProposalVersion]:
        await self.get(proposal_id, org_id)
        q = (
            select(ProposalVersion)
            .where(ProposalVersion.proposal_id == proposal_id)
            .order_by(ProposalVersion.version.desc())
        )
        return list((await self.db.execute(q)).scalars().all())

    async def _create_version_snapshot(self, proposal: Proposal, user_id: UUID) -> None:
        snapshot = {
            "title": proposal.title,
            "type": proposal.type,
            "status": proposal.status,
            "content": proposal.content,
            "total_value": float(proposal.total_value) if proposal.total_value else None,
            "version": proposal.version,
        }
        self.db.add(
            ProposalVersion(
                proposal_id=proposal.id,
                version=proposal.version,
                snapshot=snapshot,
                created_by=user_id,
            )
        )

    # ── Templates ─────────────────────────────────────────────

    async def create_template(self, org_id: UUID, data: ProposalTemplateCreate) -> ProposalTemplate:
        tmpl = ProposalTemplate(organization_id=org_id, **data.model_dump())
        self.db.add(tmpl)
        await self.db.flush()
        await self.db.refresh(tmpl)
        return tmpl

    async def get_template(self, template_id: UUID, org_id: UUID) -> ProposalTemplate:
        q = select(ProposalTemplate).where(
            ProposalTemplate.id == template_id,
            ProposalTemplate.organization_id == org_id,
        )
        tmpl = (await self.db.execute(q)).scalar_one_or_none()
        if not tmpl:
            raise NotFoundError("Proposal template")
        return tmpl

    async def list_templates(self, org_id: UUID) -> list[ProposalTemplate]:
        q = select(ProposalTemplate).where(ProposalTemplate.organization_id == org_id).order_by(ProposalTemplate.name)
        return list((await self.db.execute(q)).scalars().all())

    async def update_template(
        self, template_id: UUID, org_id: UUID, data: ProposalTemplateUpdate
    ) -> ProposalTemplate:
        tmpl = await self.get_template(template_id, org_id)
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(tmpl, k, v)
        await self.db.flush()
        await self.db.refresh(tmpl)
        return tmpl

    async def delete_template(self, template_id: UUID, org_id: UUID) -> None:
        tmpl = await self.get_template(template_id, org_id)
        await self.db.delete(tmpl)
        await self.db.flush()
