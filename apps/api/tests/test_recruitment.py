import pytest
from uuid import uuid4
from src.modules.recruitment.service import RecruitmentService
from src.modules.recruitment.schemas import JobOpeningCreate, CandidateCreate, InterviewCreate

@pytest.mark.asyncio
async def test_recruitment_flow(db):
    svc = RecruitmentService(db)
    org_id = uuid4()
    ws_id = uuid4()

    # 1. Create Job Opening
    job_data = JobOpeningCreate(title="Senior Backend Engineer", department="Engineering", employment_type="full_time")
    job = await svc.create_job(org_id, ws_id, job_data)
    assert job.title == "Senior Backend Engineer"

    # 2. Create Candidate
    c_data = CandidateCreate(job_opening_id=job.id, full_name="Jane Doe", email="jane@example.com")
    candidate = await svc.create_candidate(org_id, c_data)
    assert candidate.full_name == "Jane Doe"
    assert candidate.stage == "applied"

    # 3. Parse CV with AI
    parsed = await svc.parse_cv_with_ai(candidate.id, org_id)
    assert parsed.ai_score is not None
    assert "Automated AI CV evaluation" in parsed.ai_cv_summary

    # 4. Advance Stage
    advanced = await svc.advance_stage(candidate.id, org_id, "interview")
    assert advanced.stage == "interview"

    # 5. Schedule Interview
    int_data = InterviewCreate(interview_type="technical", notes="Technical round 1")
    interview = await svc.schedule_interview(candidate.id, org_id, int_data)
    assert interview.interview_type == "technical"
