"""
Axorks OS — CRM Resources Service

Handles polymorphic Notes, Calls, Emails, Files, unified Timeline, and Lead→Company conversion.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.companies.models import Company
from src.modules.contacts.models import Contact
from src.modules.crm.models import Call, Email, File, Note
from src.modules.crm.schemas import (
    CallCreate,
    EmailCreate,
    NoteCreate,
    TimelineEvent,
)
from src.shared.activity.models import ActivityLog


class CRMResourceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Notes ──────────────────────────────────────────────

    async def create_note(self, org_id: UUID, ws_id: UUID, user_id: UUID, data: NoteCreate) -> Note:
        note = Note(
            organization_id=org_id, workspace_id=ws_id, created_by=user_id,
            entity_type=data.entity_type, entity_id=data.entity_id,
            content=data.content, is_pinned=data.is_pinned,
        )
        self.db.add(note)
        await self.db.flush()
        await self.db.refresh(note)
        return note

    async def list_notes(self, entity_type: str, entity_id: UUID) -> list[Note]:
        q = select(Note).where(
            Note.entity_type == entity_type, Note.entity_id == entity_id, Note.deleted_at.is_(None)
        ).order_by(Note.is_pinned.desc(), Note.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    # ── Calls ──────────────────────────────────────────────

    async def create_call(self, org_id: UUID, ws_id: UUID, user_id: UUID, data: CallCreate) -> Call:
        call = Call(
            organization_id=org_id, workspace_id=ws_id, created_by=user_id,
            entity_type=data.entity_type, entity_id=data.entity_id,
            direction=data.direction, duration_seconds=data.duration_seconds,
            outcome=data.outcome, recording_url=data.recording_url, called_at=data.called_at,
        )
        self.db.add(call)
        await self.db.flush()
        await self.db.refresh(call)
        return call

    async def list_calls(self, entity_type: str, entity_id: UUID) -> list[Call]:
        q = select(Call).where(
            Call.entity_type == entity_type, Call.entity_id == entity_id,
        ).order_by(Call.called_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    # ── Emails ─────────────────────────────────────────────

    async def create_email(self, org_id: UUID, ws_id: UUID, data: EmailCreate) -> Email:
        email = Email(
            organization_id=org_id, workspace_id=ws_id,
            entity_type=data.entity_type, entity_id=data.entity_id,
            direction=data.direction, subject=data.subject, body_text=data.body_text,
            from_address=data.from_address, to_addresses=data.to_addresses,
        )
        self.db.add(email)
        await self.db.flush()
        await self.db.refresh(email)
        return email

    async def list_emails(self, entity_type: str, entity_id: UUID) -> list[Email]:
        q = select(Email).where(
            Email.entity_type == entity_type, Email.entity_id == entity_id,
        ).order_by(Email.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    # ── Files ──────────────────────────────────────────────

    async def list_files(self, entity_type: str, entity_id: UUID) -> list[File]:
        q = select(File).where(
            File.entity_type == entity_type, File.entity_id == entity_id, File.deleted_at.is_(None)
        ).order_by(File.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    # ── Unified Timeline ───────────────────────────────────

    async def get_timeline(self, entity_type: str, entity_id: UUID, limit: int = 50) -> list[TimelineEvent]:
        """Aggregate notes, calls, emails, activity logs into a single chronological stream."""
        events: list[TimelineEvent] = []

        # Notes
        for n in await self.list_notes(entity_type, entity_id):
            events.append(TimelineEvent(
                id=str(n.id), type="note",
                title="Note added",
                detail=n.content[:200] if n.content else None,
                created_at=n.created_at,
            ))

        # Calls
        for c in await self.list_calls(entity_type, entity_id):
            dur = f" ({c.duration_seconds}s)" if c.duration_seconds else ""
            events.append(TimelineEvent(
                id=str(c.id), type="call",
                title=f"Call logged{dur}",
                detail=c.outcome,
                created_at=c.called_at,
            ))

        # Emails
        for e in await self.list_emails(entity_type, entity_id):
            events.append(TimelineEvent(
                id=str(e.id), type="email",
                title=f"Email: {e.subject or '(no subject)'}",
                detail=e.direction,
                created_at=e.created_at,
            ))

        # Activity logs
        q = select(ActivityLog).where(
            ActivityLog.entity_type == entity_type, ActivityLog.entity_id == entity_id,
        ).order_by(ActivityLog.created_at.desc()).limit(limit)
        activities = list((await self.db.execute(q)).scalars().all())
        for a in activities:
            events.append(TimelineEvent(
                id=str(a.id), type="activity",
                title=a.action,
                detail=str(a.metadata) if a.metadata else None,
                created_at=a.created_at,
            ))

        events.sort(key=lambda e: e.created_at, reverse=True)
        return events[:limit]

    # ── Lead → Company Conversion ──────────────────────────

    async def convert_lead_to_company(
        self, org_id: UUID, ws_id: UUID, lead_id: UUID, user_id: UUID,
        lead_data: dict,
    ) -> tuple[Company, Contact]:
        """
        Convert a lead into a Company + primary Contact.
        """
        company = Company(
            organization_id=org_id,
            workspace_id=ws_id,
            name=lead_data.get("business_name") or "Converted Lead",
            website=lead_data.get("website"),
            industry=lead_data.get("industry"),
            country=lead_data.get("country"),
            size=lead_data.get("company_size"),
            revenue_range=lead_data.get("revenue_range"),
            linkedin_url=lead_data.get("linkedin_url"),
            lead_id=lead_id,
            owner_id=lead_data.get("owner_id"),
        )
        self.db.add(company)
        await self.db.flush()
        await self.db.refresh(company)

        contact = Contact(
            organization_id=org_id,
            workspace_id=ws_id,
            company_id=company.id,
            first_name=lead_data.get("decision_maker_name", "").split(" ")[0] if lead_data.get("decision_maker_name") else None,
            last_name=" ".join(lead_data.get("decision_maker_name", "").split(" ")[1:]) if lead_data.get("decision_maker_name") else None,
            email=lead_data.get("email"),
            phone=lead_data.get("phone"),
            title=lead_data.get("decision_maker_title"),
            is_primary=True,
            owner_id=lead_data.get("owner_id"),
        )
        self.db.add(contact)
        await self.db.flush()
        await self.db.refresh(contact)

        return company, contact
