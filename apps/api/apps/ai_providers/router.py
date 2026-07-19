from __future__ import annotations

import logging
import time
from typing import Any

from django.conf import settings

from apps.ai_providers.base import AIMessage, AIProviderError, AIResult
from apps.ai_providers.providers import (
    ClaudeProvider,
    DeepSeekProvider,
    GeminiProvider,
    OpenAIProvider,
    OpenRouterProvider,
)

logger = logging.getLogger("toolverse.ai")

MODEL_PREFIX_MAP = {
    "gpt-": "openai",
    "o1-": "openai",
    "o3-": "openai",
    "claude": "claude",
    "gemini": "gemini",
    "deepseek": "deepseek",
    "openai/": "openrouter",
    "anthropic/": "openrouter",
    "google/": "openrouter",
}


class AIRouter:
    def __init__(self) -> None:
        self._providers = {
            "openai": OpenAIProvider(api_key=getattr(settings, "OPENAI_API_KEY", "")),
            "gemini": GeminiProvider(api_key=getattr(settings, "GEMINI_API_KEY", "")),
            "claude": ClaudeProvider(api_key=getattr(settings, "ANTHROPIC_API_KEY", "")),
            "deepseek": DeepSeekProvider(api_key=getattr(settings, "DEEPSEEK_API_KEY", "")),
            "openrouter": OpenRouterProvider(api_key=getattr(settings, "OPENROUTER_API_KEY", "")),
        }

    def resolve_provider_name(self, provider: str | None, model: str | None) -> str:
        if provider and provider in self._providers:
            return provider
        if model:
            lowered = model.lower()
            for prefix, name in MODEL_PREFIX_MAP.items():
                if lowered.startswith(prefix):
                    return name
        return getattr(settings, "AI_DEFAULT_PROVIDER", "openai")

    def get_failover_chain(self, primary: str) -> list[str]:
        fallbacks = [
            p.strip()
            for p in getattr(settings, "AI_FALLBACK_PROVIDERS", "").split(",")
            if p.strip()
        ]
        chain = [primary] + [p for p in fallbacks if p != primary]
        return chain

    def complete(
        self,
        messages: list[AIMessage] | list[dict[str, str]],
        *,
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        user=None,
        tool_id: str = "",
    ) -> AIResult:
        normalized: list[AIMessage] = []
        for m in messages:
            if isinstance(m, AIMessage):
                normalized.append(m)
            else:
                normalized.append(AIMessage(role=m["role"], content=m["content"]))

        primary = self.resolve_provider_name(provider, model)
        last_error: AIProviderError | None = None
        for name in self.get_failover_chain(primary):
            impl = self._providers.get(name)
            if impl is None or not impl.is_configured():
                continue
            started = time.perf_counter()
            try:
                result = impl.complete(
                    normalized,
                    model=model if name == primary else None,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                latency_ms = (time.perf_counter() - started) * 1000
                self._log_usage(result, user=user, tool_id=tool_id, latency_ms=latency_ms)
                return result
            except AIProviderError as exc:
                logger.warning("AI provider %s failed: %s", name, exc)
                last_error = exc
                continue

        if last_error:
            raise last_error
        raise AIProviderError(
            "No AI providers are configured. Set OPENAI_API_KEY or another provider key.",
            provider=primary,
        )

    def _log_usage(self, result: AIResult, *, user: Any, tool_id: str, latency_ms: float) -> None:
        try:
            from apps.ai_providers.models import AIUsageLog

            AIUsageLog.objects.create(
                user=user if getattr(user, "is_authenticated", False) else None,
                provider=result.provider,
                model=result.model,
                tokens_in=result.tokens_in,
                tokens_out=result.tokens_out,
                cost_estimate=self._estimate_cost(result),
                tool_id=tool_id or "",
                latency_ms=latency_ms,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to persist AI usage log")

    @staticmethod
    def _estimate_cost(result: AIResult) -> float:
        # Rough USD estimate; refine per-model later
        rates = {
            "openai": (0.15, 0.60),
            "claude": (0.25, 1.25),
            "gemini": (0.10, 0.40),
            "deepseek": (0.14, 0.28),
            "openrouter": (0.20, 0.80),
        }
        inn, out = rates.get(result.provider, (0.20, 0.80))
        return round((result.tokens_in / 1_000_000) * inn + (result.tokens_out / 1_000_000) * out, 8)


_router: AIRouter | None = None


def get_ai_router() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router
