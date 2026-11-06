"""Emotion Regulation Engine: keeps modeled states bounded and safe."""

from __future__ import annotations

from typing import Any

from emotions_ai.core.state.schema import StateCollection


class EmotionRegulationEngine:
    def __init__(self, max_intensity: float = 0.95, max_states: int = 12) -> None:
        self.max_intensity = max_intensity
        self.max_states = max_states

    def regulate(self, collection: StateCollection, context: dict[str, Any] | None = None) -> StateCollection:
        # Clamp intensities
        for s in collection.states:
            s.intensity = min(s.intensity, self.max_intensity)
            # Old temporary states with very low relevance are removed
            if s.persistence_policy.value == "temporary" and s.relevance < 0.1 and s.intensity < 0.1:
                pass
        # Trim excess states: remove lowest intensity temporary first
        if len(collection.states) > self.max_states:
            ordered = sorted(collection.states, key=lambda s: (s.persistence_policy.value != "temporary", s.intensity, s.relevance))
            remove_ids = [s.state_id for s in ordered[: len(collection.states) - self.max_states]]
            for sid in remove_ids:
                collection.remove(sid)
        # Prevent runaway: if many high-intensity states, scale down
        high = [s for s in collection.states if s.intensity > 0.8]
        if len(high) > 3:
            for s in high:
                s.intensity = min(s.intensity, 0.75)
        return collection

    def behavioral_constraints(self, collection: StateCollection) -> dict[str, Any]:
        active = collection.active()
        high_arousal = any(s.arousal > 0.8 and s.intensity > 0.7 for s in active)
        sensitive = any(s.emotion in ("concern", "compassion", "sadness") and s.intensity > 0.5 for s in active)
        return {
            "avoid_humor": sensitive,
            "prioritize_support": sensitive,
            "avoid_escalation": high_arousal,
            "max_response_length_hint": "short" if sensitive else "normal",
        }