"""Evaluation tasks for native training."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EvalTask:
    name: str
    description: str
    metric: str


EMOTION_CLASSIFICATION = EvalTask(
    name="emotion_classification",
    description="Predict dominant emotion from context.",
    metric="accuracy",
)

TRANSITION_PREDICTION = EvalTask(
    name="transition_prediction",
    description="Predict resulting emotion after new information.",
    metric="accuracy",
)

STATE_PERSISTENCE = EvalTask(
    name="state_persistence",
    description="Consistency of state across sessions.",
    metric="consistency",
)


def accuracy(predictions: list[Any], targets: list[Any]) -> float:
    if not predictions or not targets:
        return 0.0
    n = min(len(predictions), len(targets))
    correct = sum(1 for i in range(n) if predictions[i] == targets[i])
    return correct / n


ALL_TASKS = [EMOTION_CLASSIFICATION, TRANSITION_PREDICTION, STATE_PERSISTENCE]