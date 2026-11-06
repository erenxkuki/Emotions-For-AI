"""Emotional transition prediction objective."""

from __future__ import annotations

from typing import Any

from emotions_ai.training.objectives.base import cross_entropy, softmax


class TransitionPredictionObjective:
    name = "transition_prediction"

    def compute(self, predictions: Any, targets: Any) -> float:
        # predictions: logits for next emotion; targets: target indices
        if not predictions or not targets:
            return 0.0
        total = 0.0
        n = min(len(predictions), len(targets))
        for i in range(n):
            probs = softmax(list(predictions[i]))
            total += cross_entropy(probs, int(targets[i]))
        return total / n