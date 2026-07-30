"""
Axorks OS — Lead Service

Lead CRUD, AI scoring, CSV import processing, bulk assignment/tagging/status updates.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.modules.ai.service import AIService
from src.modules.leads.models import Lead, LeadImport, LeadScoreHistory, LeadSource, LeadStatus
from src.modules.leads.repository import LeadRepository
from src.modules.leads.schemas import (
    CSVImportMappingRequest,
    LeadCreate,
    LeadUpdate,
)
from src.shared.activity.service import ActivityService


class LeadService:
    """Business logic service for Lead operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LeadRepository(db)
        self.ai_service = AIService()
        self.activity_service = ActivityService(db)

    async def create_lead(
        self, org_id: UUID, workspace_id: UUID, user_id: UUID, data: LeadCreate
    ) -> Lead:
        """Create lead (all fields optional!)."""
        lead_dict = data.model_dump()
        lead = Lead(
            organization_id=org_id,
            workspace_id=workspace_id,
            **lead_dict,
        )
        lead = await self.repo.create(lead)

        # Log activity
        await self.activity_service.log_activity(
            organization_id=org_id,
            workspace_id=workspace_id,
            entity_type="lead",
            entity_id=lead.id,
            actor_id=user_id,
            action="created",
            metadata={"business_name": lead.business_name, "source": lead.source.value},
        )
        return lead

    async def get_lead(self, lead_id: UUID, org_id: UUID) -> Lead:
        lead = await self.repo.get_by_id(lead_id, org_id)
        if not lead:
            raise NotFoundError("Lead", str(lead_id))
        return lead

    async def update_lead(
        self, lead_id: UUID, org_id: UUID, user_id: UUID, data: LeadUpdate
    ) -> Lead:
        lead = await self.get_lead(lead_id, org_id)
        update_data = data.model_dump(exclude_unset=True)

        lead = await self.repo.update(lead, update_data)

        # Log activity
        await self.activity_service.log_activity(
            organization_id=org_id,
            workspace_id=lead.workspace_id,
            entity_type="lead",
            entity_id=lead.id,
            actor_id=user_id,
            action="updated",
            metadata={"updated_fields": list(update_data.keys())},
        )
        return lead

    async def delete_lead(self, lead_id: UUID, org_id: UUID, user_id: UUID) -> None:
        lead = await self.get_lead(lead_id, org_id)
        await self.repo.soft_delete(lead)

        await self.activity_service.log_activity(
            organization_id=org_id,
            workspace_id=lead.workspace_id,
            entity_type="lead",
            entity_id=lead.id,
            actor_id=user_id,
            action="deleted",
        )

    async def score_lead(
        self, lead_id: UUID, org_id: UUID, user_id: UUID, explicit_score: int | None = None, reason: str | None = None
    ) -> tuple[Lead, LeadScoreHistory]:
        """Score lead manually or using AI."""
        lead = await self.get_lead(lead_id, org_id)
        old_score = lead.score

        if explicit_score is not None:
            new_score = explicit_score
            score_reason = reason or "Manual score update"
            scored_by = "manual"
        else:
            # AI scoring
            ai_res = await self.ai_service.score_lead(
                {
                    "business_name": lead.business_name,
                    "industry": lead.industry,
                    "website": lead.website,
                    "company_size": lead.company_size,
                    "decision_maker_title": lead.decision_maker_title,
                    "source": lead.source.value if lead.source else "manual",
                    "notes": lead.notes,
                    "email": lead.email,
                    "phone": lead.phone,
                }
            )
            new_score = ai_res.score
            score_reason = f"{ai_res.reasoning} Factors: {', '.join(ai_res.key_factors)}"
            scored_by = "ai"

        lead.score = new_score
        await self.db.flush()

        # Score History Record
        history = LeadScoreHistory(
            lead_id=lead.id,
            old_score=old_score,
            new_score=new_score,
            reason=score_reason,
            scored_by=scored_by,
        )
        self.db.add(history)
        await self.db.flush()

        # Log Activity
        await self.activity_service.log_activity(
            organization_id=org_id,
            workspace_id=lead.workspace_id,
            entity_type="lead",
            entity_id=lead.id,
            actor_id=user_id,
            action="scored",
            metadata={"old_score": old_score, "new_score": new_score, "scored_by": scored_by},
        )
        return lead, history

    async def get_score_history(self, lead_id: UUID) -> list[LeadScoreHistory]:
        q = select(LeadScoreHistory).where(LeadScoreHistory.lead_id == lead_id).order_by(LeadScoreHistory.created_at.desc())
        res = await self.db.execute(q)
        return list(res.scalars().all())

    async def bulk_assign(self, org_id: UUID, lead_ids: list[UUID], owner_id: UUID, actor_id: UUID) -> int:
        stmt = (
            update(Lead)
            .where(Lead.id.in_(lead_ids), Lead.organization_id == org_id, Lead.deleted_at.is_(None))
            .values(owner_id=owner_id)
        )
        res = await self.db.execute(stmt)
        return res.rowcount

    async def bulk_status(self, org_id: UUID, lead_ids: list[UUID], status: LeadStatus, actor_id: UUID) -> int:
        stmt = (
            update(Lead)
            .where(Lead.id.in_(lead_ids), Lead.organization_id == org_id, Lead.deleted_at.is_(None))
            .values(status=status)
        )
        res = await self.db.execute(stmt)
        return res.rowcount

    async def process_csv_import(
        self, org_id: UUID, workspace_id: UUID, user_id: UUID, req: CSVImportMappingRequest
    ) -> LeadImport:
        """Process CSV rows using dynamic column mapping."""
        job = LeadImport(
            organization_id=org_id,
            workspace_id=workspace_id,
            filename=req.filename,
            total_rows=len(req.csv_rows),
            status="processing",
            created_by=user_id,
        )
        self.db.add(job)
        await self.db.flush()

        imported = 0
        failed = 0
        errors = []

        mapping = req.column_mapping

        for idx, row in enumerate(req.csv_rows):
            try:
                data: dict[str, Any] = {}
                for csv_col, lead_field in mapping.items():
                    if csv_col in row and row[csv_col]:
                        val = row[csv_col].strip()
                        if lead_field == "source" and val in LeadSource.__members__.values():
                            data["source"] = LeadSource(val)
                        elif lead_field == "status" and val in LeadStatus.__members__.values():
                            data["status"] = LeadStatus(val)
                        else:
                            data[lead_field] = val

                data.setdefault("source", LeadSource.CSV)
                data["source_detail"] = f"CSV import: {req.filename}"

                lead = Lead(
                    organization_id=org_id,
                    workspace_id=workspace_id,
                    **data,
                )
                self.db.add(lead)
                imported += 1
            except Exception as e:
                failed += 1
                errors.append({"row": idx + 1, "error": str(e)})

        await self.db.flush()

        job.imported_rows = imported
        job.failed_rows = failed
        job.status = "completed"
        job.error_log = {"errors": errors[:50]} if errors else None

        await self.db.flush()
        return job
