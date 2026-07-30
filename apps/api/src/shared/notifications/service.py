"""
Axorks OS — Notification Service

CRUD operations for notifications: create, list, mark read, count unread.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.notifications.models import Notification


class NotificationService:
    """Service for managing user notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        organization_id: UUID,
        user_id: UUID,
        notification_type: str,
        title: str,
        body: str | None = None,
        link: str | None = None,
    ) -> Notification:
        """Create a new notification for a user."""
        notification = Notification(
            organization_id=organization_id,
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            link=link,
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def list_for_user(
        self,
        user_id: UUID,
        limit: int = 25,
        offset: int = 0,
        unread_only: bool = False,
    ) -> list[Notification]:
        """List notifications for a user, newest first."""
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if unread_only:
            query = query.where(Notification.read_at.is_(None))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Mark a single notification as read."""
        stmt = (
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
            .values(read_at=datetime.now(UTC))
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0  # type: ignore[union-attr]

    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all unread notifications as read for a user."""
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
            .values(read_at=datetime.now(UTC))
        )
        result = await self.db.execute(stmt)
        return result.rowcount  # type: ignore[return-value]

    async def count_unread(self, user_id: UUID) -> int:
        """Count unread notifications for a user."""
        query = select(func.count()).where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None),
        )
        result = await self.db.execute(query)
        return result.scalar_one()
