"""Cognitive Processing Engine: interpretation, questioning, discovery, realization."""

from __future__ import annotations

from typing import Any, Protocol

from emotions_ai.core.state.events import (
    CognitiveResult,
    CommonSenseAssessment,
    Experience,
)


class CognitiveProcessingEngine(Protocol):
    def process(
        self,
        experience: Experience,
        assessment: CommonSenseAssessment,
        history: list[dict[str, Any]],
        existing_states: list[Any],
    ) -> CognitiveResult: ...


class HeuristicCognitiveEngine:
    def process(
        self,
        experience: Experience,
        assessment: CommonSenseAssessment,
        history: list[dict[str, Any]],
        existing_states: list[Any],
    ) -> CognitiveResult:
        text = experience.content
        lower = text.lower()
        questions: list[str] = []
        hypotheses: list[str] = []
        contradictions: list[str] = []
        discoveries: list[str] = []
        realization: str | None = None
        interpretation_changed = False

        # Question generation for uncertainty
        if assessment.requires_clarification:
            for m in assessment.missing_information:
                questions.append(f"Could you share more about {m.replace('_', ' ')}?")

        # Discovery: achievement-like
        if assessment.situation == "achievement_or_success":
            discoveries.append("user_reported_achievement")
            realization = "The user completed something they worked toward."

        # Contradiction detection against history (simple)
        if history:
            prev_texts = " ".join(h.get("content", "") for h in history[-5:]).lower()
            # if prior difficulty then now success -> transition
            if "difficult" in prev_texts and ("completed" in lower or "finished" in lower or "achieved" in lower):
                contradictions.append("prior_difficulty_now_resolved")
                interpretation_changed = True
                realization = realization or "Earlier difficulty appears resolved by recent achievement."

        # Uncertainty propagation
        unc = assessment.uncertainty
        if "not sure" in lower or "don't know" in lower or "confused" in lower:
            unc = max(unc, 0.7)

        summary = f"situation={assessment.situation}; realization={realization or 'none'}"

        return CognitiveResult(
            questions=questions,
            hypotheses=hypotheses,
            contradictions=contradictions,
            discoveries=discoveries,
            realization=realization,
            interpretation_changed=interpretation_changed,
            uncertainty=unc,
            summary=summary,
        )