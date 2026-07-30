"""
Axorks OS — Notification API Routes

GET /api/v1/notifications         — List notifications
GET /api/v1/notifications/unread  — Count unread
PATCH /api/v1/notifications/{id}/read — Mark as read
POST /api/v1/notifications/read-all   — Mark all as read
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_tenant_context
from src.core.response import success_response
from src.core.tenant import TenantContext
from src.shared.notifications.service import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(
    limit: int = 25,
    offset: int = 0,
    unread_only: bool = False,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the current user."""
    service = NotificationService(db)
    notifications = await service.list_for_user(
        user_id=ctx.user_id,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )
    return success_response(
        data=[
            {
                "id": str(n.id),
                "type": n.type,
                "title": n.title,
                "body": n.body,
                "link": n.link,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ]
    )


@router.get("/unread")
async def get_unread_count(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Get the count of unread notifications."""
    service = NotificationService(db)
    count = await service.count_unread(ctx.user_id)
    return success_response(data={"count": count})


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Mark a single notification as read."""
    service = NotificationService(db)
    success = await service.mark_read(notification_id, ctx.user_id)
    return success_response(data={"success": success})


@router.post("/read-all")
async def mark_all_notifications_read(
    ctx: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Mark all unread notifications as read."""
    service = NotificationService(db)
    count = await service.mark_all_read(ctx.user_id)
    return success_response(data={"marked_read": count})
