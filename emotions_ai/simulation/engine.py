"""Simulation tools for inspecting emotional state evolution."""

from __future__ import annotations

import copy
from datetime import UTC, timedelta
from typing import Any

from emotions_ai.core.state.schema import StateCollection
from emotions_ai.core.temporal_evolution.engine import DefaultTemporalEvolutionEngine


class SimulationEngine:
    def __init__(self) -> None:
        self.temporal = DefaultTemporalEvolutionEngine()

    def run_timeline(
        self,
        collection: StateCollection,
        duration_seconds: float,
        step_seconds: float = 60.0,
    ) -> list[dict[str, Any]]:
        return self.temporal.simulate(collection, duration_seconds, step_seconds)

    def apply_event_sequence(
        self,
        collection: StateCollection,
        events: list[dict[str, Any]],
    ) -> StateCollection:
        col = copy.deepcopy(collection)
        now = col.updated_at
        if now.tzinfo is None:
            now = now.replace(tzinfo=UTC)
        for ev in events:
            delta = ev.get("advance_seconds", 0)
            if delta:
                now = now + timedelta(seconds=delta)
                self.temporal.apply_time(col, now)
            # caller can inject state changes externally
        col.touch(now)
        return col