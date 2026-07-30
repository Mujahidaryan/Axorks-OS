"""Axorks OS — Recruitment Router"""
from uuid import UUID
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.recruitment.schemas import CandidateCreate, CandidateRead, InterviewCreate, InterviewRead, JobOpeningCreate, JobOpeningRead
from src.modules.recruitment.service import RecruitmentService

router = APIRouter(prefix="/api/v1/recruitment", tags=["Recruitment"])


@router.post("/jobs")
async def create_job(data: JobOpeningCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    job = await svc.create_job(ctx.org_id, ctx.workspace_id, data)
    return success_response(data=JobOpeningRead.model_validate(job).model_dump(mode="json"))


@router.get("/jobs")
async def list_jobs(status: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    jobs = await svc.list_jobs(ctx.org_id, status)
    return success_response(data=[JobOpeningRead.model_validate(j).model_dump(mode="json") for j in jobs])


@router.get("/jobs/{job_id}")
async def get_job(job_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    job = await svc.get_job(job_id, ctx.org_id)
    return success_response(data=JobOpeningRead.model_validate(job).model_dump(mode="json"))


@router.post("/candidates")
async def create_candidate(data: CandidateCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    candidate = await svc.create_candidate(ctx.org_id, data)
    return success_response(data=CandidateRead.model_validate(candidate).model_dump(mode="json"))


@router.get("/candidates")
async def list_candidates(job_id: UUID | None = None, stage: str | None = None, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    candidates = await svc.list_candidates(ctx.org_id, job_id, stage)
    return success_response(data=[CandidateRead.model_validate(c).model_dump(mode="json") for c in candidates])


@router.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    candidate = await svc.get_candidate(candidate_id, ctx.org_id)
    return success_response(data=CandidateRead.model_validate(candidate).model_dump(mode="json"))


@router.post("/candidates/{candidate_id}/advance-stage")
async def advance_candidate_stage(candidate_id: UUID, stage: str = Body(..., embed=True), ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    candidate = await svc.advance_stage(candidate_id, ctx.org_id, stage)
    return success_response(data=CandidateRead.model_validate(candidate).model_dump(mode="json"))


@router.post("/candidates/{candidate_id}/parse-cv")
async def parse_cv(candidate_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    candidate = await svc.parse_cv_with_ai(candidate_id, ctx.org_id)
    return success_response(data=CandidateRead.model_validate(candidate).model_dump(mode="json"))


@router.post("/candidates/{candidate_id}/interviews")
async def schedule_interview(candidate_id: UUID, data: InterviewCreate, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    interview = await svc.schedule_interview(candidate_id, ctx.org_id, data)
    return success_response(data=InterviewRead.model_validate(interview).model_dump(mode="json"))


@router.get("/candidates/{candidate_id}/interviews")
async def list_interviews(candidate_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = RecruitmentService(db)
    interviews = await svc.list_interviews(candidate_id)
    return success_response(data=[InterviewRead.model_validate(i).model_dump(mode="json") for i in interviews])
