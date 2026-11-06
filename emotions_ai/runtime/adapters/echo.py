"""Echo adapter for testing and offline use."""

from __future__ import annotations

from typing import Any


class EchoAdapter:
    def __init__(self, name: str = "echo") -> None:
        self.name = name

    async def generate(self, messages, *, temperature=0.7, max_tokens=None, stream=False):
        last = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last = m.get("content", "")
                break
        return f"[echo] {last}"

    async def generate_stream(self, messages, *, temperature=0.7, max_tokens=None):
        text = await self.generate(messages)
        for chunk in text.split():
            yield chunk + " "

    def metadata(self) -> dict[str, Any]:
        return {"name": self.name, "capabilities": ["text"], "local": True}