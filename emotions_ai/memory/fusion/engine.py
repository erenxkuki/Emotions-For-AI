"""Memory fusion: combine LLM conversation memory with emotional memory."""

from __future__ import annotations

from emotions_ai.memory.manager import MemoryManager
from emotions_ai.memory.storage.base import MemoryRecord


class MemoryFusionEngine:
    """Fuses LLM turn memory with emotional/experience memory.

    Stores conversation turns as ``llm_turn`` memories and retrieves a merged,
    relevance-ranked context for prompt construction.
    """

    def __init__(self, memory: MemoryManager | None = None) -> None:
        self.memory = memory or MemoryManager()

    def add_turn(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        importance: float = 0.5,
    ) -> MemoryRecord | None:
        return self.memory.add(
            user_id=user_id,
            session_id=session_id,
            content=f"{role}: {content}",
            memory_type="llm_turn",
            importance=importance,
            metadata={"role": role},
        )

    def retrieve_fused(
        self,
        user_id: str,
        query: str,
        session_id: str | None = None,
        top_k: int = 8,
        include_types: list[str] | None = None,
    ) -> list[MemoryRecord]:
        types = include_types or ["experience", "emotional", "contextual", "llm_turn", "relationship"]
        records = self.memory.retrieve(
            user_id=user_id,
            query=query,
            session_id=session_id,
            top_k=top_k * 2,
            memory_types=types,
        )
        # Deduplicate by content
        seen = set()
        out: list[MemoryRecord] = []
        for r in records:
            key = r.content.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
            if len(out) >= top_k:
                break
        return out

    def build_context(self, records: list[MemoryRecord]) -> str:
        lines = []
        for r in records:
            lines.append(f"[{r.memory_type}] {r.content}")
        return "\n".join(lines)