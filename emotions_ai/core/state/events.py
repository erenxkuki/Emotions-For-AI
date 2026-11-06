"""Event definitions shared across subsystems."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    EXPERIENCE = "experience"
    MESSAGE = "message"
    DISCOVERY = "discovery"
    CONTRADICTION = "contradiction"
    GOAL_PROGRESS = "goal_progress"
    GOAL_COMPLETED = "goal_completed"
    MEMORY_ADDED = "memory_added"
    MEMORY_RETRIEVED = "memory_retrieved"
    CONTEXT_CHANGED = "context_changed"
    TIME_ELAPSED = "time_elapsed"
    STATE_TRANSITION = "state_transition"
    CLARIFICATION = "clarification"
    CORRECTION = "correction"
    CUSTOM = "custom"


class EmotionEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: EventType = EventType.CUSTOM
    user_id: str
    session_id: str = "default"
    context_id: str | None = None
    source: str = "system"
    payload: dict[str, Any] = Field(default_factory=dict)
    significance: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}


class Experience(BaseModel):
    """A structured experience fed into the engines."""

    experience_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str = "default"
    context_id: str | None = None
    content: str
    modality: str = "text"
    source: str = "user"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    significance: float | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommonSenseAssessment(BaseModel):
    situation: str = ""
    literal_meaning: str = ""
    intended_meaning: str = ""
    likely_consequences: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    uncertainty: float = Field(default=0.5, ge=0.0, le=1.0)
    social_context: str = ""
    requires_clarification: bool = False
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    notes: list[str] = Field(default_factory=list)


class CognitiveResult(BaseModel):
    questions: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    discoveries: list[str] = Field(default_factory=list)
    realization: str | None = None
    interpretation_changed: bool = False
    uncertainty: float = Field(default=0.5, ge=0.0, le=1.0)
    summary: str = ""


class ResonanceResult(BaseModel):
    perceived_user_emotions: list[str] = Field(default_factory=list)
    significance: float = Field(default=0.5, ge=0.0, le=1.0)
    empathy_level: float = Field(default=0.5, ge=0.0, le=1.0)
    suggested_internal_emotions: list[dict[str, float]] = Field(default_factory=list)
    should_mirror_intensity: bool = False
    rationale: str = ""