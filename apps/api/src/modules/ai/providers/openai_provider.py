"""
Axorks OS — OpenAI Provider Implementation
"""

from typing import AsyncIterator
import httpx
from src.core.config import get_settings
from src.modules.ai.models import AIConfig, AIResponse
from src.modules.ai.providers.base import AIProvider

settings = get_settings()


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self):
        self.api_key = settings.openai_api_key

    async def complete(self, messages: list[dict], config: AIConfig) -> AIResponse:
        model = config.model or "gpt-4o"
        if not self.api_key:
            return AIResponse(
                content="[OpenAI API key not configured. Using rule-based intelligence.]",
                model=model,
                provider=self.name,
                tokens_input=10,
                tokens_output=10,
            )

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})
            return AIResponse(
                content=choice["message"]["content"],
                model=model,
                provider=self.name,
                tokens_input=usage.get("prompt_tokens", 0),
                tokens_output=usage.get("completion_tokens", 0),
                finish_reason=choice.get("finish_reason", "stop"),
            )

    async def stream(self, messages: list[dict], config: AIConfig) -> AsyncIterator[str]:
        model = config.model or "gpt-4o"
        if not self.api_key:
            yield "Rule-based response stream simulation..."
            return

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": config.temperature,
                    "stream": True,
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        import json
                        try:
                            payload = json.loads(line[6:])
                            delta = payload["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            pass

    async def embed(self, text: str) -> list[float]:
        if not self.api_key:
            return [0.0] * 1536
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"input": text, "model": "text-embedding-3-small"},
            )
            resp.raise_for_status()
            return resp.json()["data"][0]["embedding"]
