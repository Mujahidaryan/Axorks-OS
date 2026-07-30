"""
Axorks OS — AI Provider Router
"""

from src.modules.ai.models import AIConfig
from src.modules.ai.providers.anthropic_provider import AnthropicProvider
from src.modules.ai.providers.base import AIProvider
from src.modules.ai.providers.gemini_deepseek import DeepSeekProvider, GeminiProvider
from src.modules.ai.providers.openai_provider import OpenAIProvider


class AIProviderRouter:
    """Routes AI requests based on task type or override configuration."""

    TASK_DEFAULTS = {
        "sales_assistant": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
        "suggest_questions": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
        "summarize": {"provider": "openai", "model": "gpt-4o-mini"},
        "detect_requirements": {"provider": "openai", "model": "gpt-4o"},
        "estimate_budget": {"provider": "openai", "model": "gpt-4o"},
        "estimate_complexity": {"provider": "openai", "model": "gpt-4o"},
        "suggest_tech": {"provider": "openai", "model": "gpt-4o"},
        "suggest_followup": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
        "detect_objections": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
        "action_items": {"provider": "openai", "model": "gpt-4o-mini"},
        "update_crm": {"provider": "openai", "model": "gpt-4o"},
        "proposal_generate": {"provider": "openai", "model": "gpt-4o"},
        "proposal_improve": {"provider": "openai", "model": "gpt-4o-mini"},
        "pr_review": {"provider": "openai", "model": "gpt-4o-mini"},
    }

    def __init__(self):
        self.providers: dict[str, AIProvider] = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "gemini": GeminiProvider(),
            "deepseek": DeepSeekProvider(),
        }

    def get_provider(self, task_type: str, override: AIConfig | None = None) -> tuple[AIProvider, AIConfig]:
        defaults = self.TASK_DEFAULTS.get(task_type, {"provider": "openai", "model": "gpt-4o-mini"})
        provider_name = (override and override.provider) or defaults.get("provider", "openai")
        model_name = (override and override.model) or defaults.get("model")

        provider = self.providers.get(provider_name) or self.providers["openai"]
        config = AIConfig(
            model=model_name,
            temperature=override.temperature if override else 0.7,
            max_tokens=override.max_tokens if override else 4096,
            provider=provider_name,
        )
        return provider, config
