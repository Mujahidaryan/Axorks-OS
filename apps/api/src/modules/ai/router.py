"""
Axorks OS — AI Sales Assistant API Router
"""

import json
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.modules.ai.models import (
    AIActionConfirmationRead,
    AIActionItemsRequest,
    AIDetectObjectionsRequest,
    AIDetectRequirementsRequest,
    AIEstimateBudgetRequest,
    AIEstimateComplexityRequest,
    AISuggestFollowupRequest,
    AISuggestQuestionsRequest,
    AISuggestTechRequest,
    AISummarizeRequest,
    AIUpdateCRMRequest,
)
from src.modules.ai.service import AIService

router = APIRouter(prefix="/api/v1/ai", tags=["AI Sales Assistant"])


@router.post("/sales/suggest-questions")
async def suggest_questions(req: AISuggestQuestionsRequest, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    res = await svc.suggest_questions(req.entity_type, {"name": req.entity_type, "industry": "Software"})
    return success_response(data=res)


@router.post("/sales/summarize")
async def summarize(req: AISummarizeRequest, db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    res = await svc.summarize(req.text_content or "")
    return success_response(data=res)


@router.post("/sales/detect-requirements")
async def detect_requirements(req: AIDetectRequirementsRequest, db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    res = await svc.detect_requirements(req.conversation_text)
    return success_response(data=res)


@router.post("/sales/estimate-budget")
async def estimate_budget(req: AIEstimateBudgetRequest, db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    res = await svc.estimate_budget(req.requirements, req.industry)
    return success_response(data=res)


@router.post("/sales/estimate-complexity")
async def estimate_complexity(req: AIEstimateComplexityRequest, db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    res = await svc.estimate_complexity(req.requirements)
    return success_response(data=res)


@router.post("/sales/suggest-tech")
async def suggest_tech(req: AISuggestTechRequest, db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    res = await svc.suggest_tech(req.requirements, req.preferences)
    return success_response(data=res)


@router.post("/sales/suggest-followup")
async def suggest_followup(req: AISuggestFollowupRequest, db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    res = await svc.suggest_followup(req.call_outcome, req.key_points)
    return success_response(data=res)


@router.post("/sales/detect-objections")
async def detect_objections(req: AIDetectObjectionsRequest, db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    res = await svc.detect_objections(req.transcript_text)
    return success_response(data=res)


@router.post("/sales/action-items")
async def extract_action_items(req: AIActionItemsRequest, db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    res = await svc.extract_action_items(req.conversation_text)
    return success_response(data=res)


@router.post("/sales/update-crm")
async def suggest_crm_update(req: AIUpdateCRMRequest, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    action = await svc.suggest_crm_update(ctx.org_id, ctx.workspace_id, ctx.user_id, req.entity_type, req.entity_id, req.text_source)
    return success_response(data=AIActionConfirmationRead.model_validate(action).model_dump(mode="json"))


# ── Action Confirmations ──────────────────────────────────────

@router.get("/actions")
async def list_pending_actions(entity_type: str, entity_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    actions = await svc.list_pending_actions(ctx.org_id, entity_type, entity_id)
    return success_response(data=[AIActionConfirmationRead.model_validate(a).model_dump(mode="json") for a in actions])


@router.post("/actions/{action_id}/confirm")
async def confirm_action(action_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    action = await svc.confirm_action(action_id, ctx.org_id)
    return success_response(data=AIActionConfirmationRead.model_validate(action).model_dump(mode="json"))


@router.post("/actions/{action_id}/reject")
async def reject_action(action_id: UUID, ctx: TenantContext = Depends(get_tenant_context), db: AsyncSession = Depends(get_db)):
    svc = AIService(db)
    action = await svc.reject_action(action_id, ctx.org_id)
    return success_response(data=AIActionConfirmationRead.model_validate(action).model_dump(mode="json"))


# ── SSE Stream Endpoint ──────────────────────────────────────

@router.post("/stream")
async def stream_ai(prompt: str, task_type: str = "sales_assistant"):
    svc = AIService()

    async def event_generator():
        messages = [{"role": "system", "content": "You are Axorks OS AI Sales Assistant."}, {"role": "user", "content": prompt}]
        async for chunk in svc.stream(task_type, messages):
            yield f"data: {json.dumps({'token': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
