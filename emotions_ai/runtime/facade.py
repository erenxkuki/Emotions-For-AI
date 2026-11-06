"""High-level EmotionAI facade."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from typing import Any

from emotions_ai.core.state.persistence import StatePersistence
from emotions_ai.core.state.schema import StateCollection
from emotions_ai.memory.manager import MemoryManager
from emotions_ai.runtime.adapters import (
    EchoAdapter,
    ModelAdapter,
    OpenAICompatibleAdapter,
)
from emotions_ai.runtime.orchestration.pipeline import ChatResult, Pipeline
from emotions_ai.runtime.sessions.manager import SessionManager


class EmotionAI:
    def __init__(
        self,
        model: Any = None,
        adapter: ModelAdapter | None = None,
        persistence: bool = True,
        db_path: str = ":memory:",
        temporal_evolution: bool = True,
        emotional_resonance: bool = True,
        common_sense: bool = True,
        memory: MemoryManager | None = None,
        state_persistence: StatePersistence | None = None,
        **kwargs,
    ) -> None:
        if adapter is not None:
            self.adapter = adapter
        elif isinstance(model, ModelAdapter):
            self.adapter = model
        elif isinstance(model, str):
            if model.lower().startswith("openai") or os.getenv("OPENAI_API_KEY"):
                self.adapter = OpenAICompatibleAdapter(model=model)
            else:
                self.adapter = EchoAdapter(name=model)
        else:
            self.adapter = EchoAdapter(name="default")

        self.persistence_enabled = persistence
        self.state_persistence = state_persistence
        if persistence and state_persistence is None:
            try:
                self.state_persistence = StatePersistence(db_path)
            except Exception:  # noqa: BLE001
                self.state_persistence = None
        self.memory = memory or MemoryManager()
        self.sessions = SessionManager(persistence=self.state_persistence if persistence else None)
        self.pipeline = Pipeline(adapter=self.adapter, memory=self.memory, sessions=self.sessions)

    @classmethod
    def from_config(cls, path: str) -> EmotionAI:
        import yaml

        with open(path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return cls(**cfg)

    async def chat(
        self,
        user_id: str,
        message: str,
        session_id: str = "default",
        **kwargs,
    ) -> ChatResult:
        return await self.pipeline.run(user_id=user_id, message=message, session_id=session_id, **kwargs)

    def chat_sync(self, user_id: str, message: str, session_id: str = "default", **kwargs) -> ChatResult:
        return asyncio.run(self.chat(user_id, message, session_id=session_id, **kwargs))

    async def chat_stream(self, user_id: str, message: str, session_id: str = "default", **kwargs) -> AsyncIterator[str]:
        async for chunk in self.pipeline.run_stream(user_id=user_id, message=message, session_id=session_id, **kwargs):
            yield chunk

    def get_state(self, user_id: str, session_id: str = "default") -> StateCollection:
        return self.sessions.load_state(user_id, session_id)

    def state_history(self, user_id: str, session_id: str = "default", limit: int = 50):
        if self.state_persistence is not None:
            return self.state_persistence.history(user_id, session_id, limit=limit)
        return []

    def clear_state(self, user_id: str, session_id: str = "default") -> bool:
        self.sessions.clear_state(user_id, session_id)
        if self.state_persistence is not None:
            self.state_persistence.delete(user_id, session_id)
        return True

    def delete_user_memory(self, user_id: str) -> int:
        return self.memory.delete_user(user_id)

    def export_state(self, user_id: str, session_id: str = "default") -> dict:
        col = self.get_state(user_id, session_id)
        return col.model_dump(mode="json")

    async def simulate_time(self, user_id: str, session_id: str = "default", duration_seconds: float = 3600, step_seconds: float = 300):
        col = self.get_state(user_id, session_id)
        from emotions_ai.core.temporal_evolution.engine import (
            DefaultTemporalEvolutionEngine,
        )

        eng = DefaultTemporalEvolutionEngine()
        return eng.simulate(col, duration_seconds, step_seconds)

    def close(self) -> None:
        if self.state_persistence is not None:
            self.state_persistence.close()
        if isinstance(self.memory.store, object) and hasattr(self.memory.store, "close"):
            try:
                self.memory.store.close()
            except Exception:  # noqa: BLE001, S110
                pass