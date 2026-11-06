"""Memory manager coordinating storage, retrieval and policy."""

from __future__ import annotations

import asyncio
from typing import Any

from emotions_ai.memory.policies.policy import MemoryPolicy
from emotions_ai.memory.retrieval.retriever import MemoryRetriever
from emotions_ai.memory.storage.base import MemoryRecord, MemoryStore
from emotions_ai.memory.storage.in_memory import InMemoryMemoryStore
from emotions_ai.memory.storage.sqlite import SQLiteMemoryStore


class MemoryManager:
    def __init__(
        self,
        store: MemoryStore | None = None,
        policy: MemoryPolicy | None = None,
        retriever: MemoryRetriever | None = None,
    ) -> None:
        self.store = store or InMemoryMemoryStore()
        self.policy = policy or MemoryPolicy()
        self.retriever = retriever or MemoryRetriever()

    def add(
        self,
        user_id: str,
        content: str,
        session_id: str = "default",
        memory_type: str = "experience",
        importance: float = 0.5,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        source_state_ids: list[str] | None = None,
        expires_at=None,
    ) -> MemoryRecord | None:
        record = MemoryRecord(
            user_id=user_id,
            session_id=session_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            source_state_ids=source_state_ids or [],
            expires_at=expires_at,
        )
        record = self.policy.apply_on_add(record)
        if not self.policy.should_retain(record):
            return None
        # enforce per-user cap
        existing = self.store.list_for_user(user_id)
        if len(existing) >= self.policy.max_records_per_user:
            # drop lowest importance
            victim = min(existing, key=lambda r: r.importance)
            self.store.delete(victim.memory_id, user_id)
        return self.store.add(record)

    async def aadd(self, **kwargs) -> MemoryRecord | None:
        return await asyncio.to_thread(self.add, **kwargs)

    def retrieve(
        self,
        user_id: str,
        query: str,
        session_id: str | None = None,
        top_k: int = 5,
        memory_types: list[str] | None = None,
    ) -> list[MemoryRecord]:
        records = self.store.list_for_user(user_id, session_id)
        if session_id is not None:
            # also include cross-session? Default per session; but memory persistence should allow cross-session. Include all user records.
            records = self.store.list_for_user(user_id)
        return self.retriever.retrieve(records, query, top_k=top_k, memory_types=memory_types)

    async def aretrieve(self, **kwargs) -> list[MemoryRecord]:
        return await asyncio.to_thread(self.retrieve, **kwargs)

    def delete(self, memory_id: str, user_id: str) -> bool:
        return self.store.delete(memory_id, user_id)

    async def adelete(self, memory_id: str, user_id: str) -> bool:
        return await asyncio.to_thread(self.delete, memory_id, user_id)

    def delete_user(self, user_id: str) -> int:
        return self.store.delete_user(user_id)

    def export_user(self, user_id: str) -> list[dict[str, Any]]:
        return self.store.export_user(user_id)

    def clear_session(self, user_id: str, session_id: str) -> int:
        recs = [r for r in self.store.list_for_user(user_id, session_id)]
        n = 0
        for r in recs:
            if self.store.delete(r.memory_id, user_id):
                n += 1
        return n

    @staticmethod
    def from_sqlite(db_path: str, **kwargs) -> MemoryManager:
        return MemoryManager(store=SQLiteMemoryStore(db_path), **kwargs)