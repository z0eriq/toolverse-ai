"""Base plugin contract for independently pluggable tools."""

from __future__ import annotations

from typing import Any

from django.urls import URLPattern


class BaseToolPlugin:
    """Subclass in tools/<id>/__init__.py and export as `plugin`."""

    tool_id: str = ""

    def get_urls(self) -> list[URLPattern]:
        return []

    def get_manifest(self) -> dict[str, Any] | None:
        return None

    def run_async(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Optional Celery-backed async execution. Override in plugins that need it."""
        raise NotImplementedError(f"Tool '{self.tool_id}' does not support async execution")

    def run_ai(
        self,
        messages: list[dict[str, str]],
        *,
        provider: str | None = None,
        model: str | None = None,
        user=None,
    ) -> dict[str, Any]:
        """Helper for plugins that need LLM completion via the shared AI router."""
        from apps.ai_providers.router import get_ai_router

        result = get_ai_router().complete(
            messages,
            provider=provider,
            model=model,
            user=user,
            tool_id=self.tool_id,
        )
        return {
            "content": result.content,
            "provider": result.provider,
            "model": result.model,
            "tokens_in": result.tokens_in,
            "tokens_out": result.tokens_out,
        }
