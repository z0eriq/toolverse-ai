from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class AIMessage:
    role: str  # system | user | assistant
    content: str


@dataclass
class AIResult:
    content: str
    provider: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    raw: dict[str, Any] = field(default_factory=dict)


class AIProviderError(Exception):
    """Raised when a provider call fails or is misconfigured."""

    def __init__(self, message: str, *, provider: str = "", status_code: int = 503):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


class AIProvider(Protocol):
    name: str

    def is_configured(self) -> bool: ...

    def complete(
        self,
        messages: list[AIMessage],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AIResult: ...
