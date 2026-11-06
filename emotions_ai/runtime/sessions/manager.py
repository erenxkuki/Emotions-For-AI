"""Session management and multi-user isolation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from emotions_ai.core.state.persistence import StatePersistence
from emotions_ai.core.state.schema import StateCollection


@dataclass
class Session:
    session_id: str
    user_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


class SessionManager:
    def __init__(self, persistence: StatePersistence | None = None) -> None:
        self.persistence = persistence
        self._sessions: dict[str, Session] = {}
        self._state_cache: dict[str, StateCollection] = {}

    def get_or_create(self, user_id: str, session_id: str = "default") -> Session:
        key = f"{user_id}:{session_id}"
        if key not in self._sessions:
            self._sessions[key] = Session(session_id=session_id, user_id=user_id)
        return self._sessions[key]

    def load_state(self, user_id: str, session_id: str = "default") -> StateCollection:
        key = f"{user_id}:{session_id}"
        if key in self._state_cache:
            return self._state_cache[key]
        if self.persistence is not None:
            col = self.persistence.load(user_id, session_id)
            if col is not None:
                self._state_cache[key] = col
                return col
        col = StateCollection(user_id=user_id, session_id=session_id)
        self._state_cache[key] = col
        return col

    def save_state(self, collection: StateCollection, reason: str = "update") -> None:
        key = f"{collection.user_id}:{collection.session_id}"
        self._state_cache[key] = collection
        if self.persistence is not None:
            self.persistence.save(collection, reason=reason)

    def clear_state(self, user_id: str, session_id: str = "default") -> None:
        key = f"{user_id}:{session_id}"
        self._state_cache[key] = StateCollection(user_id=user_id, session_id=session_id)
        if self.persistence is not None:
            self.persistence.delete(user_id, session_id)