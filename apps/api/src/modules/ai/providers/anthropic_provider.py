"""
Axorks OS — Anthropic Provider Implementation
"""

from typing import AsyncIterator
import httpx
from src.core.config import get_settings
from src.modules.ai.models import AIConfig, AIResponse
from src.modules.ai.providers.base import AIProvider

settings = get_settings()


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(self):
        self.api_key = settings.anthropic_api_key

    async def complete(self, messages: list[dict], config: AIConfig) -> AIResponse:
        model = config.model or "claude-3-5-sonnet-20241022"
        if not self.api_key:
            return AIResponse(
                content="[Anthropic API key not configured. Using rule-based intelligence.]",
                model=model,
                provider=self.name,
                tokens_input=10,
                tokens_output=10,
            )

        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "system": system_msg,
                    "messages": user_msgs,
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = "".join([c["text"] for c in data["content"] if c["type"] == "text"])
            usage = data.get("usage", {})
            return AIResponse(
                content=text,
                model=model,
                provider=self.name,
                tokens_input=usage.get("input_tokens", 0),
                tokens_output=usage.get("output_tokens", 0),
            )

    async def stream(self, messages: list[dict], config: AIConfig) -> AsyncIterator[str]:
        model = config.model or "claude-3-5-sonnet-20241022"
        if not self.api_key:
            yield "Rule-based response stream simulation..."
            return

        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "system": system_msg,
                    "messages": user_msgs,
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature,
                    "stream": True,
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json
                        try:
                            payload = json.loads(line[6:])
                            if payload.get("type") == "content_block_delta":
                                yield payload["delta"].get("text", "")
                        except Exception:
                            pass

    async def embed(self, text: str) -> list[float]:
        return [0.0] * 1536
