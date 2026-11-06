"""Dataset formats for native training."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EmotionTrainingSample:
    text: str
    context: str = ""
    target_emotions: list[str] = field(default_factory=list)
    target_intensity: float = 0.5
    valence: float = 0.0
    arousal: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TransitionSample:
    previous_emotions: list[str]
    new_information: str
    resulting_emotions: list[str]


def save_jsonl(samples: list[Any], path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for s in samples:
            obj = asdict(s) if hasattr(s, "__dataclass_fields__") else s
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_jsonl(path: str, cls=EmotionTrainingSample) -> list[Any]:
    out = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            try:
                out.append(cls(**obj))
            except Exception:  # noqa: BLE001
                out.append(obj)
    return out