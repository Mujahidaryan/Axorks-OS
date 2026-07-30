"""
Axorks OS — Activity Service

Creates user-facing timeline entries for entity actions.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.activity.models import ActivityLog


class ActivityService:
    """Service for creating user-facing activity timeline entries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_activity(
        self,
        organization_id: UUID,
        entity_type: str,
        entity_id: UUID,
        action: str,
        actor_id: UUID | None = None,
        workspace_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ActivityLog:
        """Create an activity log entry visible in entity timelines."""
        entry = ActivityLog(
            organization_id=organization_id,
            workspace_id=workspace_id,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            action=action,
            metadata=metadata or {},
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def get_entity_timeline(
        self,
        entity_type: str,
        entity_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ActivityLog]:
        """Get the activity timeline for a specific entity."""
        query = (
            select(ActivityLog)
            .where(
                ActivityLog.entity_type == entity_type,
                ActivityLog.entity_id == entity_id,
            )
            .order_by(ActivityLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
