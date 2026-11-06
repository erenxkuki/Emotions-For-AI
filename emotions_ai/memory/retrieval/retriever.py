"""Memory retrieval with semantic-ish, recency, importance, contextual scoring."""

from __future__ import annotations

import math
import re
from datetime import UTC, datetime

from emotions_ai.memory.storage.base import MemoryRecord


def _tokenize(text: str) -> set:
    return set(re.findall(r"[a-z0-9']+", text.lower()))


def lexical_similarity(a: str, b: str) -> float:
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class MemoryRetriever:
    def __init__(self, recency_weight: float = 0.25, importance_weight: float = 0.25, similarity_weight: float = 0.5) -> None:
        self.recency_weight = recency_weight
        self.importance_weight = importance_weight
        self.similarity_weight = similarity_weight

    def score(self, record: MemoryRecord, query: str, now: datetime | None = None) -> float:
        now = now or datetime.now(UTC)
        sim = lexical_similarity(record.content, query)
        if record.embedding is not None:
            # caller may provide query embedding externally; fallback lexical
            pass
        # recency: exponential decay over 7 days
        age = max(0.0, (now - record.created_at).total_seconds())
        recency = math.exp(-age / (7 * 86400.0))
        importance = record.importance
        total = (
            self.similarity_weight * sim
            + self.recency_weight * recency
            + self.importance_weight * importance
        )
        return total

    def retrieve(
        self,
        records: list[MemoryRecord],
        query: str,
        top_k: int = 5,
        memory_types: list[str] | None = None,
        now: datetime | None = None,
    ) -> list[MemoryRecord]:
        now = now or datetime.now(UTC)
        filtered = records
        if memory_types:
            filtered = [r for r in records if r.memory_type in memory_types]
        scored = sorted(filtered, key=lambda r: self.score(r, query, now), reverse=True)
        return scored[:top_k]