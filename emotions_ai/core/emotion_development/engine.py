"""Emotion Development Engine: develops states from experiences over time."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from emotions_ai.core.state.events import (
    CognitiveResult,
    CommonSenseAssessment,
    Experience,
    ResonanceResult,
)
from emotions_ai.core.state.schema import (
    PersistencePolicy,
    StateCollection,
    new_state,
)
from emotions_ai.core.state.taxonomy import get_registry


class EmotionDevelopmentEngine(Protocol):
    def develop(
        self,
        collection: StateCollection,
        experience: Experience,
        assessment: CommonSenseAssessment,
        cognitive: CognitiveResult,
        resonance: ResonanceResult,
        memories: list[dict[str, Any]],
        now: datetime | None = None,
    ) -> StateCollection: ...


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


class DefaultEmotionDevelopmentEngine:
    def __init__(self) -> None:
        self.registry = get_registry()

    def _policy_for(self, significance: float, situation: str) -> PersistencePolicy:
        if significance >= 0.75:
            return PersistencePolicy.LONG_LASTING if situation in ("difficulty_or_distress",) else PersistencePolicy.CONTEXTUAL
        if significance >= 0.45:
            return PersistencePolicy.CONTEXTUAL
        if significance >= 0.25:
            return PersistencePolicy.TEMPORARY
        return PersistencePolicy.TEMPORARY

    def _duration_for(self, policy: PersistencePolicy) -> float:
        return {
            PersistencePolicy.TEMPORARY: 300.0,
            PersistencePolicy.CONTEXTUAL: 3600.0,
            PersistencePolicy.LONG_LASTING: 86400.0,
            PersistencePolicy.UNRESOLVED: 7200.0,
        }.get(policy, 3600.0)

    def develop(
        self,
        collection: StateCollection,
        experience: Experience,
        assessment: CommonSenseAssessment,
        cognitive: CognitiveResult,
        resonance: ResonanceResult,
        memories: list[dict[str, Any]],
        now: datetime | None = None,
    ) -> StateCollection:
        now = now or datetime.now(UTC)
        collection.touch(now)
        significance = _clamp(
            experience.significance if experience.significance is not None else resonance.significance
        )
        uncertainty = _clamp((assessment.uncertainty + cognitive.uncertainty) / 2.0)
        confidence = _clamp(1.0 - uncertainty)
        mem_ids = [m.get("memory_id", "") for m in memories if m.get("memory_id")]

        for item in resonance.suggested_internal_emotions:
            for emotion, weight in item.items():
                w = _clamp(float(weight))
                if w <= 0:
                    continue
                # find existing state with same emotion in same context
                candidates = [
                    s for s in collection.states
                    if s.emotion == emotion and (s.context_id == experience.context_id or s.context_id is None)
                ]
                if candidates:
                    target = max(candidates, key=lambda s: s.intensity + s.relevance)
                    prev = {
                        "intensity": target.intensity,
                        "relevance": target.relevance,
                        "confidence": target.confidence,
                    }
                    # reinforcement
                    delta = w * significance * (1.0 - target.intensity) * 0.45
                    target.intensity = _clamp(target.intensity + delta)
                    target.relevance = _clamp(max(target.relevance, significance * 0.9))
                    target.confidence = _clamp((target.confidence + confidence) / 2.0)
                    target.uncertainty = _clamp((target.uncertainty + uncertainty) / 2.0)
                    target.last_reinforced_at = now
                    target.touch(now)
                    if mem_ids:
                        for mid in mem_ids:
                            if mid and mid not in target.related_memory_ids:
                                target.related_memory_ids.append(mid)
                    target.record(
                        event_type="state_reinforced",
                        source="emotion_development_engine",
                        description=f"Reinforced {emotion} from experience.",
                        evidence=[experience.content[:120]],
                        previous=prev,
                        current={
                            "intensity": target.intensity,
                            "relevance": target.relevance,
                            "confidence": target.confidence,
                        },
                        rationale="Experience significance and resonance suggested this state.",
                    )
                else:
                    policy = self._policy_for(significance, assessment.situation)
                    defaults = self.registry.defaults_for(emotion)
                    valence = defaults.get("valence", 0.0)
                    arousal = defaults.get("arousal", 0.5)
                    # adjust arousal by significance
                    arousal = _clamp(arousal * 0.6 + significance * 0.4)
                    intensity = _clamp(w * significance * 0.85 + 0.05)
                    st = new_state(
                        emotion=emotion,
                        intensity=intensity,
                        valence=valence,
                        arousal=arousal,
                        confidence=confidence,
                        relevance=significance,
                        uncertainty=uncertainty,
                        origin=f"experience:{experience.source}",
                        context_id=experience.context_id,
                        persistence_policy=policy,
                        related_memory_ids=mem_ids,
                        metadata={"experience_id": experience.experience_id},
                    )
                    st.temporal_duration = self._duration_for(policy)
                    st.record(
                        event_type="state_created",
                        source="emotion_development_engine",
                        description=f"Created {emotion} from experience.",
                        evidence=[experience.content[:120]],
                        previous={},
                        current={
                            "intensity": st.intensity,
                            "relevance": st.relevance,
                            "confidence": st.confidence,
                        },
                        rationale="Resonance suggested this internal state.",
                    )
                    collection.add(st)

        # If cognitive interpretation changed, mark affected states? Record on collection via metadata not needed.
        if cognitive.interpretation_changed:
            for s in collection.states:
                s.metadata.setdefault("interpretation_changed_at", now.isoformat())

        return collection