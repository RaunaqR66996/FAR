import sqlite3
import json
from typing import List, Optional
from datetime import datetime
from far.core.types import MemoryItem, MemoryType, TrustTier

class EpisodicStore:
    """
    EVENTS (Episodic history).
    Append-only log of what happened.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                type TEXT,
                content TEXT,
                entity_ids TEXT,
                source TEXT,
                trust_tier TEXT,
                data TEXT
            )
        """)
        self.conn.commit()

    def add_event(self, content: str, entities: List[str], source: str = "user") -> MemoryItem:
        import uuid
        item = MemoryItem(
            id=str(uuid.uuid4()),
            type=MemoryType.EVENT,
            content=content,
            entity_ids=entities,
            source=source,
            timestamp=datetime.utcnow(),
            trust_tier=TrustTier.USER
        )
        
        self.conn.execute(
            "INSERT INTO events (id, timestamp, type, content, entity_ids, source, trust_tier, data) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                item.id,
                item.timestamp.isoformat(),
                item.type,
                item.content,
                json.dumps(item.entity_ids),
                item.source,
                item.trust_tier,
                item.json()
            )
        )
        self.conn.commit()
        return item

    def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """
        Basic keyword search over events.
        """
        cursor = self.conn.execute(
            "SELECT data FROM events WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
            (f"%{query}%", limit)
        )
        results = []
        for row in cursor:
            results.append(MemoryItem.parse_raw(row[0]))
        return results
