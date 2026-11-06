"""Emotion state prediction objective."""

from __future__ import annotations

from typing import Any

from emotions_ai.training.objectives.base import cross_entropy, softmax


class EmotionStatePredictionObjective:
    name = "emotion_state_prediction"

    def compute(self, predictions: Any, targets: Any) -> float:
        # predictions: list of logits per sample; targets: list of target emotion indices
        if not predictions or not targets:
            return 0.0
        total = 0.0
        n = min(len(predictions), len(targets))
        for i in range(n):
            probs = softmax(list(predictions[i]))
            ti = int(targets[i])
            total += cross_entropy(probs, ti)
        return total / n

    def torch_loss(self):
        try:
            import torch.nn.functional as F
        except Exception as e:
            raise RuntimeError("PyTorch is required for torch_loss") from e
        return F.cross_entropy