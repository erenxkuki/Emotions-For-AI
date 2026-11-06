"""OpenAI-compatible HTTP adapter (optional httpx)."""

from __future__ import annotations

import os
from typing import Any

try:
    import httpx
except Exception:  # pragma: no cover  # noqa: BLE001
    httpx = None


class OpenAICompatibleAdapter:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        name: str = "openai_compatible",
        timeout: float = 60.0,
    ) -> None:
        self.name = name
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.timeout = timeout

    async def generate(self, messages, *, temperature=0.7, max_tokens=None, stream=False):
        if httpx is None:
            raise RuntimeError("httpx not available")
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": temperature}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

    async def generate_stream(self, messages, *, temperature=0.7, max_tokens=None):
        # Fallback: non-streaming then yield whole
        text = await self.generate(messages, temperature=temperature, max_tokens=max_tokens)
        yield text

    def metadata(self) -> dict[str, Any]:
        return {"name": self.name, "model": self.model, "base_url": self.base_url}