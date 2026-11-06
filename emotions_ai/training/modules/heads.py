"""Model heads for emotional reasoning (optional PyTorch)."""

from __future__ import annotations

try:
    import torch
    from torch import nn

    _TORCH = True
except Exception:  # noqa: BLE001
    _TORCH = False
    torch = None
    nn = None


def torch_available() -> bool:
    return _TORCH


if _TORCH:

    class EmotionHead(nn.Module):
        def __init__(self, hidden_size: int, num_emotions: int, state_dim: int = 16, dropout: float = 0.1):
            super().__init__()
            self.dropout = nn.Dropout(dropout)
            self.emotion_proj = nn.Linear(hidden_size, num_emotions)
            self.intensity_proj = nn.Linear(hidden_size, 1)
            self.state_proj = nn.Linear(hidden_size, state_dim)

        def forward(self, hidden):
            h = self.dropout(hidden)
            return {
                "emotion_logits": self.emotion_proj(h),
                "intensity": torch.sigmoid(self.intensity_proj(h)),
                "state": self.state_proj(h),
            }

else:

    class EmotionHead:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise RuntimeError("PyTorch is required for EmotionHead")

        def __call__(self, *args, **kwargs):
            raise RuntimeError("PyTorch is required for EmotionHead")