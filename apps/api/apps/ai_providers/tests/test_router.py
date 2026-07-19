import pytest
from django.test import override_settings

from apps.ai_providers.base import AIProviderError
from apps.ai_providers.router import AIRouter


@override_settings(
    OPENAI_API_KEY="",
    GEMINI_API_KEY="",
    ANTHROPIC_API_KEY="",
    DEEPSEEK_API_KEY="",
    OPENROUTER_API_KEY="",
    AI_FALLBACK_PROVIDERS="",
)
def test_router_raises_when_no_providers_configured():
    router = AIRouter()
    with pytest.raises(AIProviderError) as exc_info:
        router.complete([{"role": "user", "content": "hi"}])
    assert "No AI providers are configured" in str(exc_info.value)


@override_settings(
    OPENAI_API_KEY="",
    GEMINI_API_KEY="",
    ANTHROPIC_API_KEY="",
    DEEPSEEK_API_KEY="",
    OPENROUTER_API_KEY="",
    AI_FALLBACK_PROVIDERS="",
)
def test_router_skips_unconfigured_providers():
    router = AIRouter()
    for name, impl in router._providers.items():
        assert not impl.is_configured(), f"{name} should be unconfigured"
