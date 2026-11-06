"""Memory retention and privacy policies."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from emotions_ai.memory.storage.base import MemoryRecord

SENSITIVE_KEYWORDS = {
    "password", "secret", "token", "ssn", "credit card", "medical", "diagnosis",
}


def is_sensitive(content: str) -> bool:
    lower = content.lower()
    return any(k in lower for k in SENSITIVE_KEYWORDS)


class MemoryPolicy:
    def __init__(
        self,
        default_ttl_seconds: int | None = None,
        sensitive_ttl_seconds: int = 0,
        max_records_per_user: int = 1000,
    ) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self.sensitive_ttl_seconds = sensitive_ttl_seconds
        self.max_records_per_user = max_records_per_user

    def apply_on_add(self, record: MemoryRecord) -> MemoryRecord:
        # Do not retain sensitive info by default
        if is_sensitive(record.content):
            if self.sensitive_ttl_seconds <= 0:
                # mark for immediate expiry -> caller should skip; here set expires now
                record.expires_at = datetime.now(UTC)
            else:
                record.expires_at = datetime.now(UTC) + timedelta(seconds=self.sensitive_ttl_seconds)
            record.metadata["sensitive"] = True
        elif self.default_ttl_seconds is not None and record.expires_at is None:
            record.expires_at = datetime.now(UTC) + timedelta(seconds=self.default_ttl_seconds)
        return record

    def should_retain(self, record: MemoryRecord) -> bool:
        return not (record.expires_at is not None and record.expires_at <= datetime.now(UTC))