"""Memory-aware training objective (auxiliary)."""

from __future__ import annotations

from typing import Any


class MemoryAwareObjective:
    name = "memory_aware"

    def compute(self, predictions: Any, targets: Any) -> float:
        # Mean squared error between predicted relevance and target relevance
        if not predictions or not targets:
            return 0.0
        total = 0.0
        n = min(len(predictions), len(targets))
        for i in range(n):
            pred = float(predictions[i])
            tgt = float(targets[i])
            total += (pred - tgt) ** 2
        return total / n