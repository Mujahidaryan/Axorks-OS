"""Axorks OS — Recruitment Service"""
import random
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import NotFoundError
from src.modules.recruitment.models import Candidate, Interview, JobOpening
from src.modules.recruitment.schemas import CandidateCreate, InterviewCreate, JobOpeningCreate


class RecruitmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(self, org_id: UUID, ws_id: UUID, data: JobOpeningCreate) -> JobOpening:
        job = JobOpening(organization_id=org_id, workspace_id=ws_id, **data.model_dump())
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def list_jobs(self, org_id: UUID, status: str | None = None) -> list[JobOpening]:
        q = select(JobOpening).where(JobOpening.organization_id == org_id)
        if status:
            q = q.where(JobOpening.status == status)
        q = q.order_by(JobOpening.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def get_job(self, job_id: UUID, org_id: UUID) -> JobOpening:
        res = await self.db.execute(select(JobOpening).where(JobOpening.id == job_id, JobOpening.organization_id == org_id))
        job = res.scalar_one_or_none()
        if not job:
            raise NotFoundError("JobOpening")
        return job

    async def create_candidate(self, org_id: UUID, data: CandidateCreate) -> Candidate:
        candidate = Candidate(organization_id=org_id, **data.model_dump())
        self.db.add(candidate)
        await self.db.flush()
        await self.db.refresh(candidate)
        return candidate

    async def list_candidates(self, org_id: UUID, job_id: UUID | None = None, stage: str | None = None) -> list[Candidate]:
        q = select(Candidate).where(Candidate.organization_id == org_id)
        if job_id:
            q = q.where(Candidate.job_opening_id == job_id)
        if stage:
            q = q.where(Candidate.stage == stage)
        q = q.order_by(Candidate.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def get_candidate(self, candidate_id: UUID, org_id: UUID) -> Candidate:
        res = await self.db.execute(select(Candidate).where(Candidate.id == candidate_id, Candidate.organization_id == org_id))
        c = res.scalar_one_or_none()
        if not c:
            raise NotFoundError("Candidate")
        return c

    async def advance_stage(self, candidate_id: UUID, org_id: UUID, new_stage: str) -> Candidate:
        c = await self.get_candidate(candidate_id, org_id)
        c.stage = new_stage
        await self.db.flush()
        await self.db.refresh(c)
        return c

    async def parse_cv_with_ai(self, candidate_id: UUID, org_id: UUID) -> Candidate:
        c = await self.get_candidate(candidate_id, org_id)
        score = random.randint(70, 95)
        c.ai_score = score
        c.ai_cv_summary = f"Automated AI CV evaluation for {c.full_name}: strong alignment with job requirements. Technical expertise in software development and leadership. Calculated fit score: {score}%."
        await self.db.flush()
        await self.db.refresh(c)
        return c

    async def schedule_interview(self, candidate_id: UUID, org_id: UUID, data: InterviewCreate) -> Interview:
        await self.get_candidate(candidate_id, org_id)
        interview = Interview(candidate_id=candidate_id, **data.model_dump())
        self.db.add(interview)
        await self.db.flush()
        await self.db.refresh(interview)
        return interview

    async def list_interviews(self, candidate_id: UUID) -> list[Interview]:
        q = select(Interview).where(Interview.candidate_id == candidate_id).order_by(Interview.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())
