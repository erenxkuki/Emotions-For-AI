"""Response Expression Engine: converts internal states to communication guidance."""

from __future__ import annotations

from typing import Any

from emotions_ai.core.emotion_regulation.engine import EmotionRegulationEngine
from emotions_ai.core.state.schema import StateCollection


class ResponseExpressionEngine:
    def __init__(self) -> None:
        self.regulator = EmotionRegulationEngine()

    def guidance(self, collection: StateCollection) -> dict[str, Any]:
        constraints = self.regulator.behavioral_constraints(collection)
        active = collection.active()
        # Determine tone
        tone = "neutral"
        if any(s.emotion in ("concern", "compassion", "sadness") and s.intensity > 0.4 for s in active):
            tone = "supportive"
        elif any(s.emotion in ("happiness", "excitement", "joy") and s.intensity > 0.4 for s in active):
            tone = "enthusiastic"
        elif any(s.emotion in ("curiosity", "confusion", "uncertainty") and s.intensity > 0.4 for s in active):
            tone = "inquisitive"
        # Formality/pacing
        pacing = "normal"
        if constraints.get("prioritize_support"):
            pacing = "patient"
        length = constraints.get("max_response_length_hint", "normal")
        return {
            "tone": tone,
            "pacing": pacing,
            "response_length": length,
            "avoid_humor": constraints.get("avoid_humor", False),
            "prioritize_support": constraints.get("prioritize_support", False),
            "avoid_escalation": constraints.get("avoid_escalation", False),
            "active_emotions": [s.emotion for s in active],
            "guidance_text": self._guidance_text(tone, constraints),
        }

    def _guidance_text(self, tone: str, constraints: dict[str, Any]) -> str:
        parts = [f"Adopt a {tone} tone."]
        if constraints.get("prioritize_support"):
            parts.append("Prioritize understanding and support; avoid minimizing the user's experience.")
        if constraints.get("avoid_humor"):
            parts.append("Avoid humor; the context may be sensitive.")
        if constraints.get("avoid_escalation"):
            parts.append("Keep arousal low; avoid escalating emotional intensity.")
        parts.append("Be accurate and helpful; do not fabricate personal experiences.")
        return " ".join(parts)

    def build_system_prompt(self, guidance: dict[str, Any], emotional_summary: dict[str, Any]) -> str:
        return (
            "You are an AI assistant with modeled emotional context. "
            f"Communication guidance: {guidance['guidance_text']} "
            f"Active modeled emotions: {guidance['active_emotions']}. "
            "Emotional states are computational representations, not subjective feelings. "
            "Do not claim to personally suffer or feel. Prioritize factual accuracy and user wellbeing."
        )