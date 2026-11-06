"""Hugging Face Transformers integration helpers (optional)."""

from __future__ import annotations

from emotions_ai.training.config import EmotionConfig


def requires_transformers():
    try:
        import transformers  # noqa: F401

        return True
    except Exception:  # noqa: BLE001
        return False


def build_emotion_model(base_model_name: str, config: EmotionConfig | None = None):
    config = config or EmotionConfig()
    if not requires_transformers():
        raise RuntimeError("transformers is required for build_emotion_model")
    try:
        from transformers import AutoModel
    except Exception as e:
        raise RuntimeError("torch and transformers are required") from e
    base = AutoModel.from_pretrained(base_model_name)
    # Attach a simple head via attribute (non-invasive)
    from emotions_ai.training.modules.heads import EmotionHead

    head = EmotionHead(config.hidden_size, config.num_emotions, config.state_dim, config.dropout)
    base.emotion_head = head
    return base


def training_step(model, batch, objective) -> float:
    """Minimal training step returning loss (requires torch)."""
    try:
        import torch  # noqa: F401
    except Exception as e:
        raise RuntimeError("torch is required") from e
    model.train()
    outputs = model(**batch)
    # Expect batch to contain 'labels'
    logits = outputs.get("emotion_logits") if isinstance(outputs, dict) else None
    if logits is None:
        raise ValueError("Model output missing emotion_logits")
    loss = objective.compute(logits.detach().cpu().tolist(), batch["labels"].tolist())
    return float(loss)