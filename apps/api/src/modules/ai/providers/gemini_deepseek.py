"""
Axorks OS — Google Gemini & DeepSeek Providers
"""

from typing import AsyncIterator
import httpx
from src.core.config import get_settings
from src.modules.ai.models import AIConfig, AIResponse
from src.modules.ai.providers.base import AIProvider

settings = get_settings()


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self):
        self.api_key = settings.google_api_key

    async def complete(self, messages: list[dict], config: AIConfig) -> AIResponse:
        model = config.model or "gemini-1.5-pro"
        return AIResponse(
            content="[Gemini Provider initialized. Using rule-based fallback.]",
            model=model,
            provider=self.name,
            tokens_input=10,
            tokens_output=10,
        )

    async def stream(self, messages: list[dict], config: AIConfig) -> AsyncIterator[str]:
        yield "Gemini stream simulation..."

    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768


class DeepSeekProvider(AIProvider):
    name = "deepseek"

    def __init__(self):
        self.api_key = getattr(settings, "deepseek_api_key", None)

    async def complete(self, messages: list[dict], config: AIConfig) -> AIResponse:
        model = config.model or "deepseek-chat"
        return AIResponse(
            content="[DeepSeek Provider initialized. Using rule-based fallback.]",
            model=model,
            provider=self.name,
            tokens_input=10,
            tokens_output=10,
        )

    async def stream(self, messages: list[dict], config: AIConfig) -> AsyncIterator[str]:
        yield "DeepSeek stream simulation..."

    async def embed(self, text: str) -> list[float]:
        return [0.0] * 1536
