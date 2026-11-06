"""Emotional Resonance Engine: interpret another's experience without mere mirroring."""

from __future__ import annotations

from typing import Any, Protocol

from emotions_ai.core.state.events import (
    CommonSenseAssessment,
    Experience,
    ResonanceResult,
)


class EmotionalResonanceEngine(Protocol):
    def resonate(
        self,
        experience: Experience,
        assessment: CommonSenseAssessment,
        cognitive: Any,
        history: list[dict[str, Any]],
    ) -> ResonanceResult: ...


class HeuristicResonanceEngine:
    """Interprets the user's emotional context and suggests internal modeled states.

    Does not mirror intensity by default; emphasizes understanding and support.
    """

    def resonate(
        self,
        experience: Experience,
        assessment: CommonSenseAssessment,
        cognitive: Any,
        history: list[dict[str, Any]],
    ) -> ResonanceResult:
        perceived: list[str] = []
        suggested: list[dict[str, float]] = []
        significance = 0.5
        empathy = 0.5

        if assessment.situation == "difficulty_or_distress":
            perceived.append("sadness")
            suggested.append({"concern": 0.6})
            suggested.append({"attentiveness": 0.5})
            suggested.append({"compassion": 0.5})
            significance = 0.75
            empathy = 0.7
        elif assessment.situation == "achievement_or_success":
            perceived.append("happiness")
            suggested.append({"happiness": 0.5})
            suggested.append({"excitement": 0.4})
            suggested.append({"appreciation": 0.4})
            significance = 0.7
            empathy = 0.6
        else:
            suggested.append({"curiosity": 0.3})
            suggested.append({"attentiveness": 0.4})
            significance = 0.4
            empathy = 0.4

        # High uncertainty -> concern/attentiveness
        if getattr(cognitive, "uncertainty", 0.5) > 0.6:
            suggested.append({"concern": 0.3})

        # Do not mirror intensity
        mirror = False

        rationale = (
            "Interpreted user context; suggested internal states emphasize understanding "
            "rather than mirroring."
        )
        return ResonanceResult(
            perceived_user_emotions=perceived,
            significance=significance,
            empathy_level=empathy,
            suggested_internal_emotions=suggested,
            should_mirror_intensity=mirror,
            rationale=rationale,
        )