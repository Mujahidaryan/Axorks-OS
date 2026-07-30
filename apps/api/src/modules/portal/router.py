"""
Axorks OS — Client Portal API Router
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.response import success_response
from src.modules.portal.schemas import (
    PortalLoginRequest, PortalUserRead, SupportTicketCreate,
    SupportTicketRead, TicketMessageCreate, TicketMessageRead,
)
from src.modules.portal.service import PortalService
from src.modules.projects.schemas import ProjectRead
from src.modules.proposals.schemas import ProposalRead

router = APIRouter(prefix="/api/v1/portal", tags=["Client Portal"])


@router.post("/login")
async def portal_login(data: PortalLoginRequest, db: AsyncSession = Depends(get_db)):
    svc = PortalService(db)
    user, token = await svc.login(data)
    return success_response(data={
        "user": PortalUserRead.model_validate(user).model_dump(mode="json"),
        "token": token,
    })


@router.get("/company/{company_id}/projects")
async def get_client_projects(company_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PortalService(db)
    projects = await svc.get_client_projects(company_id)
    return success_response(data=[ProjectRead.model_validate(p).model_dump(mode="json") for p in projects])


@router.get("/company/{company_id}/proposals")
async def get_client_proposals(company_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PortalService(db)
    props = await svc.get_client_proposals(company_id)
    return success_response(data=[ProposalRead.model_validate(p).model_dump(mode="json") for p in props])


@router.post("/company/{company_id}/tickets")
async def create_ticket(company_id: UUID, data: SupportTicketCreate, portal_user_id: UUID, org_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PortalService(db)
    ticket = await svc.create_ticket(org_id, company_id, portal_user_id, data)
    return success_response(data=SupportTicketRead.model_validate(ticket).model_dump(mode="json"))


@router.get("/company/{company_id}/tickets")
async def list_tickets(company_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PortalService(db)
    tickets = await svc.list_tickets(company_id)
    return success_response(data=[SupportTicketRead.model_validate(t).model_dump(mode="json") for t in tickets])


@router.post("/tickets/{ticket_id}/messages")
async def add_ticket_message(ticket_id: UUID, data: TicketMessageCreate, sender_name: str = "Client", sender_type: str = "client", db: AsyncSession = Depends(get_db)):
    svc = PortalService(db)
    msg = await svc.add_ticket_message(ticket_id, sender_type, sender_name, data)
    return success_response(data=TicketMessageRead.model_validate(msg).model_dump(mode="json"))
