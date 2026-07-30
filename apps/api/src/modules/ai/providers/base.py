"""
Axorks OS — Base AI Provider Abstract Interface
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator
from src.modules.ai.models import AIConfig, AIResponse


class AIProvider(ABC):
    """Abstract base class for all LLM providers (OpenAI, Anthropic, Gemini, DeepSeek)."""

    name: str

    @abstractmethod
    async def complete(self, messages: list[dict], config: AIConfig) -> AIResponse:
        """Executes a single completion call."""
        pass

    @abstractmethod
    async def stream(self, messages: list[dict], config: AIConfig) -> AsyncIterator[str]:
        """Streams token responses asynchronously."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generates embedding vector for input text."""
        pass
