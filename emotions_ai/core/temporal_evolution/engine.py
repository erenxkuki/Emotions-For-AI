"""Temporal Emotion Evolution: event-driven + time-driven hybrid."""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any, Protocol

from emotions_ai.core.state.schema import EmotionalState, StateCollection


class TemporalEvolutionEngine(Protocol):
    def apply_time(self, collection: StateCollection, now: datetime) -> StateCollection: ...
    def simulate(self, collection: StateCollection, duration_seconds: float, step_seconds: float) -> list[dict[str, Any]]: ...


POLICY_HALF_LIFE = {
    "temporary": 300.0,
    "contextual": 3600.0,
    "long_lasting": 86400.0,
    "unresolved": 7200.0,
}


def _half_life(state: EmotionalState) -> float:
    base = POLICY_HALF_LIFE.get(state.persistence_policy.value, 3600.0)
    # relevance extends persistence
    return base * (0.5 + state.relevance)


class DefaultTemporalEvolutionEngine:
    def apply_time(self, collection: StateCollection, now: datetime) -> StateCollection:
        # compute elapsed since updated_at per state? Use collection.updated_at as last global update.
        last = collection.updated_at
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        if now.tzinfo is None:
            now = now.replace(tzinfo=UTC)
        dt = max(0.0, (now - last).total_seconds())
        if dt <= 0:
            collection.touch(now)
            return collection

        to_remove: list[str] = []
        for s in collection.states:
            hl = _half_life(s)
            # exponential decay of intensity and relevance
            factor = math.exp(-math.log(2) * dt / max(hl, 1.0))
            # unresolved states decay slower, temporary faster (already via half-life)
            s.intensity = max(0.0, s.intensity * factor)
            s.relevance = max(0.0, s.relevance * (0.5 + 0.5 * factor))
            # uncertainty grows slightly as time passes without reinforcement
            s.uncertainty = min(1.0, s.uncertainty + 0.001 * (dt / 60.0))
            s.touch(now)
            if s.intensity < 0.02 and s.persistence_policy.value == "temporary":
                to_remove.append(s.state_id)
        for sid in to_remove:
            collection.remove(sid)
        collection.touch(now)
        return collection

    def apply_event(self, collection: StateCollection, event: Any, now: datetime | None = None) -> StateCollection:
        now = now or datetime.now(UTC)
        # Event-driven: bump relevance of states matching context
        ctx = getattr(event, "context_id", None)
        for s in collection.states:
            if ctx and s.context_id == ctx:
                s.relevance = min(1.0, s.relevance + 0.1)
                s.touch(now)
        collection.touch(now)
        return collection

    def simulate(
        self,
        collection: StateCollection,
        duration_seconds: float,
        step_seconds: float,
    ) -> list[dict[str, Any]]:
        # Work on a copy
        import copy

        col = copy.deepcopy(collection)
        now = col.updated_at
        if now.tzinfo is None:
            now = now.replace(tzinfo=UTC)
        timeline: list[dict[str, Any]] = []
        steps = int(duration_seconds / step_seconds) if step_seconds > 0 else 0
        for i in range(steps + 1):
            timeline.append({"t": i * step_seconds, "states": col.summary()["active"]})
            now = now.replace(tzinfo=UTC) if now.tzinfo is None else now
            from datetime import timedelta

            now = now + timedelta(seconds=step_seconds)
            self.apply_time(col, now)
        return timeline