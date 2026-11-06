"""SQLite-backed memory store."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

from emotions_ai.memory.storage.base import MemoryRecord


class SQLiteMemoryStore:
    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init()

    def _init(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                expires_at TEXT,
                tags TEXT NOT NULL,
                metadata TEXT NOT NULL,
                source_state_ids TEXT NOT NULL,
                embedding TEXT
            )
            """
        )
        self._conn.commit()

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            memory_id=row["memory_id"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            memory_type=row["memory_type"],
            content=row["content"],
            importance=row["importance"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
            source_state_ids=json.loads(row["source_state_ids"]),
            embedding=json.loads(row["embedding"]) if row["embedding"] else None,
        )

    def add(self, record: MemoryRecord) -> MemoryRecord:
        self._conn.execute(
            """INSERT OR REPLACE INTO memories
            (memory_id,user_id,session_id,memory_type,content,importance,created_at,updated_at,expires_at,tags,metadata,source_state_ids,embedding)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                record.memory_id,
                record.user_id,
                record.session_id,
                record.memory_type,
                record.content,
                record.importance,
                record.created_at.isoformat(),
                record.updated_at.isoformat(),
                record.expires_at.isoformat() if record.expires_at else None,
                json.dumps(record.tags),
                json.dumps(record.metadata),
                json.dumps(record.source_state_ids),
                json.dumps(record.embedding) if record.embedding is not None else None,
            ),
        )
        self._conn.commit()
        return record

    def get(self, memory_id: str, user_id: str) -> MemoryRecord | None:
        cur = self._conn.execute(
            "SELECT * FROM memories WHERE memory_id=? AND user_id=?", (memory_id, user_id)
        )
        row = cur.fetchone()
        if row is None:
            return None
        rec = self._row_to_record(row)
        if rec.expires_at is not None and rec.expires_at < datetime.now(UTC):
            self.delete(memory_id, user_id)
            return None
        return rec

    def list_for_user(self, user_id: str, session_id: str | None = None) -> list[MemoryRecord]:
        if session_id is None:
            cur = self._conn.execute("SELECT * FROM memories WHERE user_id=?", (user_id,))
        else:
            cur = self._conn.execute(
                "SELECT * FROM memories WHERE user_id=? AND session_id=?", (user_id, session_id)
            )
        out = []
        for row in cur.fetchall():
            rec = self._row_to_record(row)
            if rec.expires_at is not None and rec.expires_at < datetime.now(UTC):
                continue
            out.append(rec)
        return out

    def update(self, record: MemoryRecord) -> MemoryRecord:
        record.updated_at = datetime.now(UTC)
        return self.add(record)

    def delete(self, memory_id: str, user_id: str) -> bool:
        cur = self._conn.execute(
            "DELETE FROM memories WHERE memory_id=? AND user_id=?", (memory_id, user_id)
        )
        self._conn.commit()
        return cur.rowcount > 0

    def delete_user(self, user_id: str) -> int:
        cur = self._conn.execute("DELETE FROM memories WHERE user_id=?", (user_id,))
        self._conn.commit()
        return cur.rowcount

    def export_user(self, user_id: str) -> list[dict[str, Any]]:
        return [r.model_dump(mode="json") for r in self.list_for_user(user_id)]

    def close(self) -> None:
        self._conn.close()