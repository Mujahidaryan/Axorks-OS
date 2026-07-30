"""
Axorks OS — Audit Service

Logs all entity mutations with old/new values for compliance and debugging.
"""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.audit.models import AuditLog


class AuditService:
    """Service for creating immutable audit log entries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        organization_id: UUID,
        user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """
        Create an audit log entry.

        Args:
            organization_id: The tenant organization
            user_id: The user performing the action
            action: What happened (e.g., 'created', 'updated', 'deleted')
            entity_type: The type of entity (e.g., 'organization', 'lead', 'user')
            entity_id: The ID of the affected entity
            old_values: Previous state (for updates/deletes)
            new_values: New state (for creates/updates)
            ip_address: Client IP address
            user_agent: Client user agent string
        """
        entry = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry
