"""Emotion Transformation Engine: gradual, context-dependent state transitions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from emotions_ai.core.state.schema import StateCollection


class EmotionTransformationEngine(Protocol):
    def evaluate(
        self,
        collection: StateCollection,
        cognitive: Any,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]: ...
    def apply(
        self,
        collection: StateCollection,
        transitions: list[dict[str, Any]],
        now: datetime | None,
    ) -> StateCollection: ...


# Candidate transitions are suggestions, not inevitable rules.
_TRANSITION_MAP = {
    "surprise": ["curiosity"],
    "uncertainty": ["confidence", "curiosity"],
    "frustration": ["satisfaction", "relief"],
    "anticipation": ["relief", "satisfaction"],
    "concern": ["compassion", "attentiveness"],
    "confusion": ["curiosity", "confidence"],
}


class DefaultTransformationEngine:
    def evaluate(
        self,
        collection: StateCollection,
        cognitive: Any,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        transitions: list[dict[str, Any]] = []
        interpretation_changed = getattr(cognitive, "interpretation_changed", False)
        discoveries = getattr(cognitive, "discoveries", []) or []

        for state in list(collection.states):
            if state.intensity < 0.1:
                continue
            # Transformation when new info resolves prior state
            if interpretation_changed and state.emotion in _TRANSITION_MAP:
                for target in _TRANSITION_MAP[state.emotion]:
                    # Only transform if evidence supports
                    evidence_ok = bool(discoveries) or interpretation_changed
                    if not evidence_ok:
                        continue
                    transitions.append(
                        {
                            "from_state_id": state.state_id,
                            "from_emotion": state.emotion,
                            "to_emotion": target,
                            "reason": "interpretation_changed",
                            "confidence": min(0.9, state.confidence),
                            "gradual": True,
                        }
                    )
            # Uncertainty reduction -> confidence
            if state.emotion == "uncertainty" and getattr(cognitive, "uncertainty", 1.0) < 0.4:
                transitions.append(
                    {
                        "from_state_id": state.state_id,
                        "from_emotion": "uncertainty",
                        "to_emotion": "confidence",
                        "reason": "uncertainty_reduced",
                        "confidence": 0.7,
                        "gradual": True,
                    }
                )
        # Deduplicate by from->to
        seen = set()
        out = []
        for t in transitions:
            key = (t["from_state_id"], t["to_emotion"])
            if key in seen:
                continue
            seen.add(key)
            out.append(t)
        return out

    def apply(
        self,
        collection: StateCollection,
        transitions: list[dict[str, Any]],
        now: datetime | None = None,
    ) -> StateCollection:
        now = now or datetime.now(UTC)
        for t in transitions:
            src = collection.get(t["from_state_id"])
            if src is None:
                continue
            # Gradual: reduce source intensity, create/raise target
            src.intensity = max(0.0, src.intensity - 0.15)
            src.record(
                event_type="state_transition",
                source="emotion_transformation_engine",
                description=f"{src.emotion} -> {t['to_emotion']}",
                evidence=[],
                previous={"intensity": src.intensity + 0.15},
                current={"intensity": src.intensity},
                rationale=t.get("reason", ""),
            )
            # find or create target state
            targets = [s for s in collection.states if s.emotion == t["to_emotion"]]
            if targets:
                tgt = targets[0]
                tgt.intensity = min(1.0, tgt.intensity + 0.15)
                tgt.relevance = max(tgt.relevance, src.relevance)
                tgt.touch(now)
                tgt.record(
                    event_type="state_transition",
                    source="emotion_transformation_engine",
                    description=f"raised by transition from {src.emotion}",
                    rationale=t.get("reason", ""),
                )
            else:
                from emotions_ai.core.state.schema import new_state

                ns = new_state(
                    emotion=t["to_emotion"],
                    intensity=0.3,
                    origin="transformation",
                    context_id=src.context_id,
                    persistence_policy=src.persistence_policy,
                )
                ns.record(
                    event_type="state_created",
                    source="emotion_transformation_engine",
                    description=f"Created via transition from {src.emotion}",
                    rationale=t.get("reason", ""),
                )
                collection.add(ns)
            # remove source if negligible
            if src.intensity < 0.05:
                collection.remove(src.state_id)
        collection.touch(now)
        return collection