import sqlite3
import json
from typing import List, Optional
from far.core.types import MemoryItem, MemoryType, TrustTier

class SemanticStore:
    """
    FACTS (Semantic Layer).
    Stores immutable truths and entities.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        # Facts table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id TEXT PRIMARY KEY,
                content TEXT,
                entity_ids TEXT,
                relations TEXT, 
                trust_tier TEXT,
                data TEXT
            )
        """)
        self.conn.commit()

    def add_fact(self, content: str, entities: List[str], relations: dict = None) -> MemoryItem:
        import uuid
        item = MemoryItem(
            id=str(uuid.uuid4()),
            type=MemoryType.FACT,
            content=content,
            entity_ids=entities,
            source="system",
            trust_tier=TrustTier.SYSTEM,
            metadata={"relations": relations or {}}
        )
        
        self.conn.execute(
            "INSERT INTO facts (id, content, entity_ids, relations, trust_tier, data) VALUES (?, ?, ?, ?, ?, ?)",
            (
                item.id,
                item.content,
                json.dumps(item.entity_ids),
                json.dumps(relations or {}),
                item.trust_tier,
                item.json()
            )
        )
        self.conn.commit()
        return item

    def get_by_entity(self, entity_id: str) -> List[MemoryItem]:
        """
        Retrieve facts about a specific entity.
        """
        # In a real implementation with NetworkX, we would traverse the graph.
        # Here we do a simple LIKE query on the JSON list.
        cursor = self.conn.execute(
            "SELECT data FROM facts WHERE entity_ids LIKE ?",
            (f"%{entity_id}%",)
        )
        results = []
        for row in cursor:
            results.append(MemoryItem.parse_raw(row[0]))
        return results

    def search(self, query: str) -> List[MemoryItem]:
        cursor = self.conn.execute(
            "SELECT data FROM facts WHERE content LIKE ? LIMIT 10",
            (f"%{query}%",)
        )
        return [MemoryItem.parse_raw(row[0]) for row in cursor]
