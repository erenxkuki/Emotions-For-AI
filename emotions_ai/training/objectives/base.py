"""Base training objectives."""

from __future__ import annotations

from typing import Any, Protocol


class TrainingObjective(Protocol):
    name: str

    def compute(self, predictions: Any, targets: Any) -> float: ...


def softmax(logits: list[float]) -> list[float]:
    import math

    m = max(logits) if logits else 0.0
    exps = [math.exp(x - m) for x in logits]
    s = sum(exps) or 1.0
    return [e / s for e in exps]


def cross_entropy(predicted_probs: list[float], target_index: int) -> float:
    p = predicted_probs[target_index] if 0 <= target_index < len(predicted_probs) else 1e-9
    import math

    return -math.log(max(p, 1e-9))