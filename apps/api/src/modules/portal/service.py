"""
Axorks OS — Client Portal Service
"""

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError, UnauthorizedError
from src.core.security import hash_password, verify_password, create_access_token
from src.modules.portal.models import PortalUser, SupportTicket, TicketMessage
from src.modules.portal.schemas import PortalLoginRequest, SupportTicketCreate, TicketMessageCreate
from src.modules.projects.models import Project
from src.modules.proposals.models import Proposal


class PortalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_portal_user(self, org_id: UUID, company_id: UUID, name: str, email: str, password: str) -> PortalUser:
        user = PortalUser(
            organization_id=org_id,
            company_id=company_id,
            name=name,
            email=email,
            password_hash=hash_password(password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def login(self, data: PortalLoginRequest) -> tuple[PortalUser, str]:
        q = select(PortalUser).where(PortalUser.email == data.email, PortalUser.is_active.is_(True))
        res = await self.db.execute(q)
        user = res.scalar_one_or_none()
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid client portal credentials")

        token = create_access_token({"sub": str(user.id), "org_id": str(user.organization_id), "company_id": str(user.company_id), "role": "client"})
        return user, token

    # ── Scoped Client Data Access ──────────────────────────────

    async def get_client_projects(self, company_id: UUID) -> list[Project]:
        q = select(Project).where(Project.company_id == company_id, Project.deleted_at.is_(None)).order_by(Project.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def get_client_proposals(self, company_id: UUID) -> list[Proposal]:
        q = select(Proposal).where(Proposal.company_id == company_id, Proposal.deleted_at.is_(None)).order_by(Proposal.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    # ── Support Tickets ──────────────────────────────────────

    async def create_ticket(self, org_id: UUID, company_id: UUID, portal_user_id: UUID, data: SupportTicketCreate) -> SupportTicket:
        ticket = SupportTicket(
            organization_id=org_id,
            company_id=company_id,
            portal_user_id=portal_user_id,
            **data.model_dump(),
        )
        self.db.add(ticket)
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket

    async def list_tickets(self, company_id: UUID) -> list[SupportTicket]:
        q = select(SupportTicket).where(SupportTicket.company_id == company_id).order_by(SupportTicket.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def add_ticket_message(self, ticket_id: UUID, sender_type: str, sender_name: str, data: TicketMessageCreate) -> TicketMessage:
        msg = TicketMessage(
            ticket_id=ticket_id,
            sender_type=sender_type,
            sender_name=sender_name,
            message=data.message,
        )
        self.db.add(msg)
        await self.db.flush()
        await self.db.refresh(msg)
        return msg
