"""In-memory memory store."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from emotions_ai.memory.storage.base import MemoryRecord


class InMemoryMemoryStore:
    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}

    def add(self, record: MemoryRecord) -> MemoryRecord:
        self._records[record.memory_id] = record
        return record

    def get(self, memory_id: str, user_id: str) -> MemoryRecord | None:
        r = self._records.get(memory_id)
        if r is None or r.user_id != user_id:
            return None
        if r.expires_at is not None and r.expires_at < datetime.now(UTC):
            del self._records[memory_id]
            return None
        return r

    def list_for_user(self, user_id: str, session_id: str | None = None) -> list[MemoryRecord]:
        now = datetime.now(UTC)
        out = []
        for r in list(self._records.values()):
            if r.user_id != user_id:
                continue
            if session_id is not None and r.session_id != session_id:
                continue
            if r.expires_at is not None and r.expires_at < now:
                continue
            out.append(r)
        return out

    def update(self, record: MemoryRecord) -> MemoryRecord:
        record.updated_at = datetime.now(UTC)
        self._records[record.memory_id] = record
        return record

    def delete(self, memory_id: str, user_id: str) -> bool:
        r = self._records.get(memory_id)
        if r is None or r.user_id != user_id:
            return False
        del self._records[memory_id]
        return True

    def delete_user(self, user_id: str) -> int:
        ids = [mid for mid, r in self._records.items() if r.user_id == user_id]
        for mid in ids:
            del self._records[mid]
        return len(ids)

    def export_user(self, user_id: str) -> list[dict[str, Any]]:
        return [r.model_dump(mode="json") for r in self.list_for_user(user_id)]