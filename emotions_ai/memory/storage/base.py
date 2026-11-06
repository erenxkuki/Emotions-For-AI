"""Memory storage interfaces."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Protocol

from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    memory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str = "default"
    memory_type: str = "experience"
    content: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_state_ids: list[str] = Field(default_factory=list)
    embedding: list[float] | None = None

    model_config = {"arbitrary_types_allowed": True}


class MemoryStore(Protocol):
    def add(self, record: MemoryRecord) -> MemoryRecord: ...
    def get(self, memory_id: str, user_id: str) -> MemoryRecord | None: ...
    def list_for_user(self, user_id: str, session_id: str | None = None) -> list[MemoryRecord]: ...
    def update(self, record: MemoryRecord) -> MemoryRecord: ...
    def delete(self, memory_id: str, user_id: str) -> bool: ...
    def delete_user(self, user_id: str) -> int: ...
    def export_user(self, user_id: str) -> list[dict[str, Any]]: ...