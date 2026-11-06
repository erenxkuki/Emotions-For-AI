"""Common Sense Engine: interface plus a lightweight heuristic implementation."""

from __future__ import annotations

import re
from typing import Any, Protocol

from emotions_ai.core.state.events import CommonSenseAssessment, Experience


class CommonSenseEngine(Protocol):
    def assess(self, experience: Experience, history: list[dict[str, Any]]) -> CommonSenseAssessment: ...


_KEYWORDS_DIFFICULT = {"difficult", "hard", "struggling", "sad", "upset", "lost", "problem", "issue", "tired", "overwhelmed"}
_KEYWORDS_ACHIEVEMENT = {"completed", "finished", "achieved", "won", "success", "passed", "graduated", "launched"}
_KEYWORDS_QUESTION = {"?", "how", "why", "what", "when", "where", "who"}


class HeuristicCommonSenseEngine:
    """A deterministic, dependency-free common-sense assessor.

    Not a substitute for a real knowledge base; provides structured output and
    uncertainty flags so callers can decide whether to escalate.
    """

    def assess(self, experience: Experience, history: list[dict[str, Any]]) -> CommonSenseAssessment:
        text = experience.content.lower()
        words = set(re.findall(r"[a-z']+", text))
        situation = "general_conversation"
        if words & _KEYWORDS_ACHIEVEMENT:
            situation = "achievement_or_success"
        elif words & _KEYWORDS_DIFFICULT:
            situation = "difficulty_or_distress"
        elif "?" in text:
            situation = "question"

        missing: list[str] = []
        if len(text.split()) < 4:
            missing.append("more_context")
        if situation == "difficulty_or_distress" and not any(w in text for w in ["because", "due", "after"]):
            missing.append("cause_of_distress")

        intended = text
        consequences: list[str] = []
        if situation == "achievement_or_success":
            consequences.append("positive_reinforcement_appropriate")
            consequences.append("acknowledge_effort")
        elif situation == "difficulty_or_distress":
            consequences.append("avoid_minimizing")
            consequences.append("offer_support")
            consequences.append("avoid_unsolicited_advice")

        uncertainty = 0.3
        if missing:
            uncertainty = min(0.8, 0.3 + 0.2 * len(missing))
        if len(history) == 0:
            uncertainty = min(0.9, uncertainty + 0.1)

        requires_clarification = bool(missing) and uncertainty > 0.6

        social_context = "neutral"
        if situation == "difficulty_or_distress":
            social_context = "sensitive"
        elif situation == "achievement_or_success":
            social_context = "celebratory"

        return CommonSenseAssessment(
            situation=situation,
            literal_meaning=experience.content,
            intended_meaning=intended,
            likely_consequences=consequences,
            missing_information=missing,
            uncertainty=uncertainty,
            social_context=social_context,
            requires_clarification=requires_clarification,
            confidence=1.0 - uncertainty,
            notes=["heuristic_assessment"],
        )