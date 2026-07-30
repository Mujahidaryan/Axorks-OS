"""Axorks OS — Integrations Service"""
import base64
from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.exceptions import NotFoundError
from src.modules.integrations.catalog import INTEGRATION_CATALOG
from src.modules.integrations.models import Integration, Webhook
from src.modules.integrations.schemas import IntegrationConnect, WebhookCreate


class IntegrationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _encrypt(val: str | None) -> str | None:
        if not val:
            return None
        return base64.b64encode(val.encode()).decode()

    def get_catalog((self)) -> dict:
        return INTEGRATION_CATALOG

    async def connect(self, org_id: UUID, data: IntegrationConnect) -> Integration:
        res = await self.db.execute(
            select(Integration).where(Integration.organization_id == org_id, Integration.provider == data.provider)
        )
        existing = res.scalar_one_or_none()

        cat_info = INTEGRATION_CATALOG.get(data.provider, {})
        category = data.category or cat_info.get("category", "general")

        enc_access = self._encrypt(data.access_token)
        enc_refresh = self._encrypt(data.refresh_token)

        if existing:
            existing.status = "connected"
            existing.access_token_encrypted = enc_access
            existing.refresh_token_encrypted = enc_refresh
            existing.account_identifier = data.account_identifier
            existing.scopes = data.scopes
            existing.category = category
            existing.connected_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(existing)
            return existing

        integration = Integration(
            organization_id=org_id,
            provider=data.provider,
            category=category,
            status="connected",
            access_token_encrypted=enc_access,
            refresh_token_encrypted=enc_refresh,
            account_identifier=data.account_identifier,
            scopes=data.scopes,
            connected_at=datetime.utcnow(),
        )
        self.db.add(integration)
        await self.db.flush()
        await self.db.refresh(integration)
        return integration

    async def disconnect(self, org_id: UUID, provider: str) -> None:
        res = await self.db.execute(
            select(Integration).where(Integration.organization_id == org_id, Integration.provider == provider)
        )
        item = res.scalar_one_or_none()
        if not item:
            raise NotFoundError("Integration")
        item.status = "disconnected"
        item.access_token_encrypted = None
        item.refresh_token_encrypted = None
        await self.db.flush()

    async def list_connected(self, org_id: UUID) -> list[Integration]:
        q = select(Integration).where(Integration.organization_id == org_id, Integration.status == "connected")
        return list((await self.db.execute(q)).scalars().all())

    async def create_webhook(self, org_id: UUID, data: WebhookCreate) -> Webhook:
        webhook = Webhook(organization_id=org_id, **data.model_dump())
        self.db.add(webhook)
        await self.db.flush()
        await self.db.refresh(webhook)
        return webhook

    async def list_webhooks(self, org_id: UUID) -> list[Webhook]:
        q = select(Webhook).where(Webhook.organization_id == org_id).order_by(Webhook.created_at.desc())
        return list((await self.db.execute(q)).scalars().all())

    async def delete_webhook(self, webhook_id: UUID, org_id: UUID) -> None:
        res = await self.db.execute(select(Webhook).where(Webhook.id == webhook_id, Webhook.organization_id == org_id))
        webhook = res.scalar_one_or_none()
        if not webhook:
            raise NotFoundError("Webhook")
        await self.db.delete(webhook)
        await self.db.flush()