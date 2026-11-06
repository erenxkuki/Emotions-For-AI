"""Persistent storage for emotional state collections."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import Any

from emotions_ai.core.state.schema import StateCollection


class StatePersistence:
    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init()

    def _init(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS state_collections (
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (user_id, session_id)
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS state_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                reason TEXT
            )
            """
        )
        self._conn.commit()

    def save(self, collection: StateCollection, reason: str = "update") -> None:
        payload = collection.model_dump_json()
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """INSERT INTO state_collections (user_id,session_id,payload,updated_at)
               VALUES (?,?,?,?)
               ON CONFLICT(user_id,session_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at""",
            (collection.user_id, collection.session_id, payload, now),
        )
        self._conn.execute(
            "INSERT INTO state_history (user_id,session_id,payload,recorded_at,reason) VALUES (?,?,?,?,?)",
            (collection.user_id, collection.session_id, payload, now, reason),
        )
        self._conn.commit()

    def load(self, user_id: str, session_id: str = "default") -> StateCollection | None:
        cur = self._conn.execute(
            "SELECT payload FROM state_collections WHERE user_id=? AND session_id=?",
            (user_id, session_id),
        )
        row = cur.fetchone()
        if row is None:
            return None
        try:
            return StateCollection.model_validate_json(row["payload"])
        except Exception:  # noqa: BLE001
            return None

    def history(self, user_id: str, session_id: str = "default", limit: int = 50) -> list[dict[str, Any]]:
        cur = self._conn.execute(
            "SELECT payload, recorded_at, reason FROM state_history WHERE user_id=? AND session_id=? ORDER BY id DESC LIMIT ?",
            (user_id, session_id, limit),
        )
        out = []
        for row in cur.fetchall():
            try:
                col = StateCollection.model_validate_json(row["payload"])
                out.append({"recorded_at": row["recorded_at"], "reason": row["reason"], "summary": col.summary()})
            except Exception:  # noqa: BLE001, S112
                continue
        return out

    def delete(self, user_id: str, session_id: str = "default") -> bool:
        cur = self._conn.execute(
            "DELETE FROM state_collections WHERE user_id=? AND session_id=?", (user_id, session_id)
        )
        self._conn.commit()
        return cur.rowcount > 0

    def delete_user(self, user_id: str) -> int:
        cur = self._conn.execute("DELETE FROM state_collections WHERE user_id=?", (user_id,))
        self._conn.execute("DELETE FROM state_history WHERE user_id=?", (user_id,))
        self._conn.commit()
        return cur.rowcount

    def list_sessions(self, user_id: str) -> list[str]:
        cur = self._conn.execute(
            "SELECT session_id FROM state_collections WHERE user_id=?", (user_id,)
        )
        return [r["session_id"] for r in cur.fetchall()]

    def close(self) -> None:
        self._conn.close()