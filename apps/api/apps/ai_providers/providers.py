from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from django.conf import settings

from apps.ai_providers.base import AIMessage, AIProviderError, AIResult


def _http_json(
    url: str,
    *,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise AIProviderError(f"HTTP {exc.code}: {body[:500]}", status_code=exc.code) from exc
    except urllib.error.URLError as exc:
        raise AIProviderError(f"Network error: {exc.reason}") from exc


class OpenAICompatibleProvider:
    """Shared OpenAI-style chat completions client (OpenAI, DeepSeek, OpenRouter)."""

    name = "openai"
    default_model = "gpt-4o-mini"
    base_url = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str = "", base_url: str | None = None, default_model: str | None = None):
        self.api_key = api_key
        if base_url:
            self.base_url = base_url
        if default_model:
            self.default_model = default_model

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def complete(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AIResult:
        if not self.is_configured():
            raise AIProviderError(f"{self.name} API key is not configured", provider=self.name)
        used_model = model or self.default_model
        payload = {
            "model": used_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.name == "openrouter":
            headers["HTTP-Referer"] = getattr(settings, "AI_OPENROUTER_REFERER", "https://toolverse.ai")
            headers["X-Title"] = "ToolVerse AI"

        raw = _http_json(self.base_url, headers=headers, payload=payload)
        try:
            content = raw["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(f"Unexpected {self.name} response shape", provider=self.name) from exc
        usage = raw.get("usage") or {}
        return AIResult(
            content=content or "",
            provider=self.name,
            model=used_model,
            tokens_in=int(usage.get("prompt_tokens") or 0),
            tokens_out=int(usage.get("completion_tokens") or 0),
            raw=raw,
        )


class OpenAIProvider(OpenAICompatibleProvider):
    name = "openai"
    default_model = "gpt-4o-mini"
    base_url = "https://api.openai.com/v1/chat/completions"


class DeepSeekProvider(OpenAICompatibleProvider):
    name = "deepseek"
    default_model = "deepseek-chat"
    base_url = "https://api.deepseek.com/chat/completions"


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    default_model = "openai/gpt-4o-mini"
    base_url = "https://openrouter.ai/api/v1/chat/completions"


class ClaudeProvider:
    name = "claude"
    default_model = "claude-3-5-haiku-latest"
    base_url = "https://api.anthropic.com/v1/messages"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def complete(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AIResult:
        if not self.is_configured():
            raise AIProviderError("Anthropic API key is not configured", provider=self.name)
        used_model = model or self.default_model
        system = "\n".join(m.content for m in messages if m.role == "system")
        chat = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
        if not chat:
            chat = [{"role": "user", "content": "Hello"}]
        payload: dict[str, Any] = {
            "model": used_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat,
        }
        if system:
            payload["system"] = system
        raw = _http_json(
            self.base_url,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            payload=payload,
        )
        try:
            blocks = raw.get("content") or []
            content = "".join(b.get("text", "") for b in blocks if isinstance(b, dict))
        except (TypeError, AttributeError) as exc:
            raise AIProviderError("Unexpected Claude response shape", provider=self.name) from exc
        usage = raw.get("usage") or {}
        return AIResult(
            content=content,
            provider=self.name,
            model=used_model,
            tokens_in=int(usage.get("input_tokens") or 0),
            tokens_out=int(usage.get("output_tokens") or 0),
            raw=raw,
        )


class GeminiProvider:
    name = "gemini"
    default_model = "gemini-2.0-flash"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def complete(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AIResult:
        if not self.is_configured():
            raise AIProviderError("Gemini API key is not configured", provider=self.name)
        used_model = model or self.default_model
        # Flatten to Gemini contents format
        contents = []
        system_bits = []
        for m in messages:
            if m.role == "system":
                system_bits.append(m.content)
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m.content}]})
        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hello"}]}]
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{used_model}:generateContent?key={self.api_key}"
        )
        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_bits:
            payload["systemInstruction"] = {"parts": [{"text": "\n".join(system_bits)}]}
        raw = _http_json(url, headers={"Content-Type": "application/json"}, payload=payload)
        try:
            content = raw["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("Unexpected Gemini response shape", provider=self.name) from exc
        usage = raw.get("usageMetadata") or {}
        return AIResult(
            content=content,
            provider=self.name,
            model=used_model,
            tokens_in=int(usage.get("promptTokenCount") or 0),
            tokens_out=int(usage.get("candidatesTokenCount") or 0),
            raw=raw,
        )
