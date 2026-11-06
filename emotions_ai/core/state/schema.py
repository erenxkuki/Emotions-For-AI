"""Standardized, versioned emotional state representations."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

SCHEMA_VERSION = "1.0"


class PersistencePolicy(str, Enum):
    TEMPORARY = "temporary"
    CONTEXTUAL = "contextual"
    LONG_LASTING = "long_lasting"
    UNRESOLVED = "unresolved"


class StateDevelopmentEvent(BaseModel):
    """An auditable record of how a state changed."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: str
    source: str
    description: str = ""
    evidence: list[str] = Field(default_factory=list)
    previous: dict[str, Any] = Field(default_factory=dict)
    current: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""

    model_config = {"frozen": False}


class EmotionalState(BaseModel):
    """A single modeled emotional state.

    Multiple states may coexist. Values are bounded and deterministic updates
    are recorded in ``development_history``.
    """

    schema_version: str = SCHEMA_VERSION
    state_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    emotion: str
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    arousal: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    uncertainty: float = Field(default=0.5, ge=0.0, le=1.0)
    origin: str = "unknown"
    context_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_reinforced_at: datetime | None = None
    persistence_policy: PersistencePolicy = PersistencePolicy.CONTEXTUAL
    temporal_duration: float | None = None  # expected persistence in seconds
    development_history: list[StateDevelopmentEvent] = Field(default_factory=list)
    related_memory_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("emotion")
    @classmethod
    def _emotion_nonempty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("emotion must be non-empty")
        return v.strip().lower()

    def touch(self, now: datetime | None = None) -> None:
        self.updated_at = now or datetime.now(UTC)

    def record(
        self,
        event_type: str,
        source: str,
        description: str = "",
        evidence: list[str] | None = None,
        previous: dict[str, Any] | None = None,
        current: dict[str, Any] | None = None,
        rationale: str = "",
    ) -> StateDevelopmentEvent:
        ev = StateDevelopmentEvent(
            event_type=event_type,
            source=source,
            description=description,
            evidence=evidence or [],
            previous=previous or {},
            current=current or {},
            rationale=rationale,
        )
        self.development_history.append(ev)
        return ev

    def snapshot(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    model_config = {"arbitrary_types_allowed": True}


class StateCollection(BaseModel):
    """Container for multiple simultaneous states for a user/session."""

    schema_version: str = SCHEMA_VERSION
    user_id: str
    session_id: str
    states: list[EmotionalState] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def get(self, state_id: str) -> EmotionalState | None:
        for s in self.states:
            if s.state_id == state_id:
                return s
        return None

    def by_emotion(self, emotion: str) -> list[EmotionalState]:
        return [s for s in self.states if s.emotion == emotion.lower()]

    def add(self, state: EmotionalState) -> None:
        self.states.append(state)
        self.touch()

    def remove(self, state_id: str) -> bool:
        before = len(self.states)
        self.states = [s for s in self.states if s.state_id != state_id]
        if len(self.states) != before:
            self.touch()
            return True
        return False

    def touch(self, now: datetime | None = None) -> None:
        self.updated_at = now or datetime.now(UTC)

    def clear(self) -> None:
        self.states = []
        self.touch()

    def active(self, min_intensity: float = 0.05) -> list[EmotionalState]:
        return [s for s in self.states if s.intensity >= min_intensity]

    def summary(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "state_count": len(self.states),
            "active": [
                {
                    "state_id": s.state_id,
                    "emotion": s.emotion,
                    "intensity": round(s.intensity, 4),
                    "valence": round(s.valence, 4),
                    "arousal": round(s.arousal, 4),
                    "relevance": round(s.relevance, 4),
                    "confidence": round(s.confidence, 4),
                    "uncertainty": round(s.uncertainty, 4),
                    "origin": s.origin,
                    "persistence_policy": s.persistence_policy.value,
                }
                for s in self.active()
            ],
        }


def new_state(
    emotion: str,
    intensity: float = 0.5,
    valence: float | None = None,
    arousal: float | None = None,
    confidence: float = 0.5,
    relevance: float = 0.5,
    uncertainty: float = 0.5,
    origin: str = "unknown",
    context_id: str | None = None,
    persistence_policy: PersistencePolicy = PersistencePolicy.CONTEXTUAL,
    related_memory_ids: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> EmotionalState:
    return EmotionalState(
        emotion=emotion,
        intensity=intensity,
        valence=valence if valence is not None else 0.0,
        arousal=arousal if arousal is not None else 0.5,
        confidence=confidence,
        relevance=relevance,
        uncertainty=uncertainty,
        origin=origin,
        context_id=context_id,
        persistence_policy=persistence_policy,
        related_memory_ids=related_memory_ids or [],
        metadata=metadata or {},
    )