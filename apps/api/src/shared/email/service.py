"""
Axorks OS — Email Service (Resend)

Sends transactional email via Resend API. Logs to stdout when API key is not configured.
"""

import logging

import httpx

from src.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class EmailService:
    """Send email via Resend with graceful fallback in development."""

    async def send(
        self,
        to: str | list[str],
        subject: str,
        html: str,
        *,
        reply_to: str | None = None,
    ) -> dict:
        recipients = [to] if isinstance(to, str) else to
        if not settings.resend_api_key:
            logger.info(
                "Resend not configured — email simulated to=%s subject=%s",
                recipients,
                subject,
            )
            return {"id": "simulated", "status": "simulated"}

        payload: dict = {
            "from": settings.resend_from_email,
            "to": recipients,
            "subject": subject,
            "html": html,
        }
        if reply_to:
            payload["reply_to"] = reply_to

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
