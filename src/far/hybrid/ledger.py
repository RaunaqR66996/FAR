"""Immutable event ledger ("The Spine")."""
from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional

from .logging_config import get_logger
from .types import EventRecord

logger = get_logger(__name__)


class ImmutableEventLedger:
    """Append-only log with lightweight indexing."""

    def __init__(self, db_path: str = "far_spine_events.db", connection: Optional[sqlite3.Connection] = None):
        self.db_path = db_path
        self._conn = connection
        if self.db_path == ":memory:" and self._conn is None:
            # Allow thread sharing for in-memory simulation
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn:
            return self._conn
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _initialize_schema(self) -> None:
        """Initialize the relational schema with indexes."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS event_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entity_id ON event_log (entity_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON event_log (timestamp)")
            logger.debug("Event ledger schema ready.")

    def record_event(self, entity_id: str, event_type: str, payload: Dict[str, Any]) -> int:
        """Atomically commit an event to the ledger."""
        ts = payload.get("timestamp") or self._current_time()
        payload_json = json.dumps(payload)
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO event_log (entity_id, event_type, payload, timestamp) VALUES (?, ?, ?, ?)",
                (entity_id, event_type, payload_json, ts),
            )
            logger.info("Recorded event %s for entity %s", event_type, entity_id)
            return cursor.lastrowid

    def replay_history(self, entity_id: str) -> List[EventRecord]:
        """Reconstruct the causal history of an entity."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, entity_id, event_type, payload, timestamp FROM event_log WHERE entity_id = ? ORDER BY id ASC",
                (entity_id,),
            )
            return [
                EventRecord(row[0], row[1], row[2], json.loads(row[3]), row[4])
                for row in cursor.fetchall()
            ]

    @staticmethod
    def _current_time() -> float:
        import time

        return time.time()
