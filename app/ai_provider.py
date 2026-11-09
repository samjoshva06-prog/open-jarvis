from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ProviderError(RuntimeError):
    """Raised when the configured chat-completions provider fails."""


class OpenAICompatibleProvider:
    """Small OpenAI Chat Completions-compatible client using Python's stdlib."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        self.timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "45"))

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def respond(self, messages: list[dict[str, str]]) -> str:
        if not self.is_configured:
            raise ProviderError("AI provider is not configured")
        payload = json.dumps({"model": self.model, "messages": messages}).encode("utf-8")
        request = Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
            raise ProviderError("The AI provider could not complete the request") from error
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ProviderError("The AI provider returned an unexpected response") from error
        if not isinstance(content, str) or not content.strip():
            raise ProviderError("The AI provider returned an empty response")
        return content.strip()
