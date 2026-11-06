"""Configuration for native training integration."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EmotionConfig(BaseModel):
    emotional_reasoning: bool = True
    emotional_persistence: bool = True
    common_sense: bool = True
    temporal_evolution: bool = True
    emotional_resonance: bool = True
    custom_emotions: list[str] = Field(default_factory=list)
    state_dim: int = Field(default=16, ge=1)
    num_emotions: int = Field(default=32, ge=1)
    hidden_size: int = Field(default=768, ge=1)
    dropout: float = Field(default=0.1, ge=0.0, le=1.0)

    def to_dict(self) -> dict:
        return self.model_dump()