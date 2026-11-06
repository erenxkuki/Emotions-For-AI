"""Flexible emotional taxonomy with default categories and custom registration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmotionDefinition:
    id: str
    label: str
    category: str
    default_valence: float = 0.0
    default_arousal: float = 0.5
    description: str = ""


DEFAULT_EMOTIONS: list[EmotionDefinition] = [
    # Positive
    EmotionDefinition("happiness", "Happiness", "positive", 0.8, 0.6, "Positive affect from favorable outcomes."),
    EmotionDefinition("joy", "Joy", "positive", 0.9, 0.7, "Intense positive affect."),
    EmotionDefinition("excitement", "Excitement", "positive", 0.7, 0.85, "High arousal positive anticipation."),
    EmotionDefinition("satisfaction", "Satisfaction", "positive", 0.6, 0.4, "Contentment after goal progress."),
    EmotionDefinition("amusement", "Amusement", "positive", 0.6, 0.55, "Light positive affect, humor."),
    EmotionDefinition("appreciation", "Appreciation", "positive", 0.65, 0.45, "Recognition of value."),
    EmotionDefinition("hope", "Hope", "positive", 0.5, 0.45, "Positive expectation."),
    EmotionDefinition("curiosity", "Curiosity", "positive", 0.4, 0.55, "Drive to explore/understand."),
    EmotionDefinition("confidence", "Confidence", "positive", 0.5, 0.4, "Belief in capability."),
    EmotionDefinition("relief", "Relief", "positive", 0.5, 0.3, "Reduction of concern."),
    # Negative
    EmotionDefinition("sadness", "Sadness", "negative", -0.7, 0.3, "Low valence, low arousal."),
    EmotionDefinition("anger", "Anger", "negative", -0.6, 0.8, "High arousal negative."),
    EmotionDefinition("frustration", "Frustration", "negative", -0.5, 0.65, "Blocked goal."),
    EmotionDefinition("fear", "Fear", "negative", -0.7, 0.8, "Threat response."),
    EmotionDefinition("disappointment", "Disappointment", "negative", -0.5, 0.4, "Unmet expectation."),
    EmotionDefinition("anxiety", "Anxiety", "negative", -0.5, 0.7, "Uncertainty about future."),
    EmotionDefinition("loneliness", "Loneliness", "negative", -0.6, 0.35, "Social disconnection."),
    EmotionDefinition("confusion", "Confusion", "negative", -0.2, 0.5, "Lack of understanding."),
    # Social/relational
    EmotionDefinition("compassion", "Compassion", "social", 0.3, 0.45, "Concern for others."),
    EmotionDefinition("concern", "Concern", "social", -0.1, 0.45, "Worry about another."),
    EmotionDefinition("empathy_response", "Empathy-related response", "social", 0.2, 0.45, "Resonant understanding."),
    EmotionDefinition("trust", "Trust", "social", 0.5, 0.3, "Reliance/confidence in other."),
    EmotionDefinition("gratitude", "Gratitude", "social", 0.7, 0.4, "Appreciation for help."),
    EmotionDefinition("respect", "Respect", "social", 0.4, 0.35, "Esteem for other."),
    EmotionDefinition("attentiveness", "Attentiveness", "social", 0.2, 0.5, "Focused engagement."),
    # Complex/mixed
    EmotionDefinition("nostalgia", "Nostalgia", "complex", 0.2, 0.35, "Bittersweet memory."),
    EmotionDefinition("surprise", "Surprise", "complex", 0.1, 0.75, "Unexpected event."),
    EmotionDefinition("anticipation", "Anticipation", "complex", 0.4, 0.6, "Looking forward."),
    EmotionDefinition("ambivalence", "Ambivalence", "complex", 0.0, 0.5, "Mixed feelings."),
    EmotionDefinition("awe", "Awe", "complex", 0.5, 0.6, "Vastness/wonder."),
    EmotionDefinition("relief_sadness", "Relief mixed with sadness", "complex", 0.1, 0.4, "Mixed relief/sadness."),
    EmotionDefinition("uncertainty", "Uncertainty", "complex", -0.1, 0.5, "Unresolved not-knowing."),
]


class EmotionRegistry:
    def __init__(self) -> None:
        self._items: dict[str, EmotionDefinition] = {}
        for e in DEFAULT_EMOTIONS:
            self.register(e, overwrite=True)

    def register(self, definition: EmotionDefinition, overwrite: bool = False) -> None:
        if definition.id in self._items and not overwrite:
            raise ValueError(f"Emotion '{definition.id}' already registered")
        self._items[definition.id] = definition

    def get(self, emotion_id: str) -> EmotionDefinition | None:
        return self._items.get(emotion_id.lower())

    def all(self) -> list[EmotionDefinition]:
        return list(self._items.values())

    def ids(self) -> list[str]:
        return list(self._items.keys())

    def categories(self) -> list[str]:
        return sorted({e.category for e in self._items.values()})

    def is_known(self, emotion_id: str) -> bool:
        return emotion_id.lower() in self._items

    def defaults_for(self, emotion_id: str) -> dict[str, float]:
        d = self.get(emotion_id)
        if d is None:
            return {"valence": 0.0, "arousal": 0.5}
        return {"valence": d.default_valence, "arousal": d.default_arousal}


_GLOBAL_REGISTRY = EmotionRegistry()


def get_registry() -> EmotionRegistry:
    return _GLOBAL_REGISTRY