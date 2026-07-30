"""
Axorks OS — Settings Service
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organizations.service import OrgService
from src.modules.workspaces.service import WorkspaceService


class SettingsService:
    """Service for modifying Org and Workspace settings."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_service = OrgService(db)
        self.ws_service = WorkspaceService(db)

    async def update_org_settings(self, org_id: UUID, settings_data: dict, user_id: UUID) -> dict:
        org = await self.org_service.get(org_id)
        current = org.settings or {}
        current.update({k: v for k, v in settings_data.items() if v is not None})
        org.settings = current
        await self.db.flush()
        return org.settings

    async def update_workspace_settings(self, workspace_id: UUID, org_id: UUID, settings_data: dict) -> dict:
        ws = await self.ws_service.get(workspace_id, org_id)
        current = ws.settings or {}
        current.update({k: v for k, v in settings_data.items() if v is not None})
        ws.settings = current
        await self.db.flush()
        return ws.settings
