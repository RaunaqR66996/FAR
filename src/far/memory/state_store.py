from typing import Dict, Optional, List
from datetime import datetime
from far.core.types import MemoryItem, MemoryType, TrustTier

class StateStore:
    """
    CURRENT STATE (Live operational status).
    In-memory KV store for fast access to 'now'.
    """
    def __init__(self):
        self._store: Dict[str, MemoryItem] = {}

    def upsert(self, key: str, value: str, source: str, metadata: Dict = None) -> MemoryItem:
        """
        Updates the state for a given key.
        """
        item_id = f"state::{key}"
        item = MemoryItem(
            id=item_id,
            type=MemoryType.STATE,
            content=value,
            source=source,
            timestamp=datetime.utcnow(),
            as_of=datetime.utcnow(),
            trust_tier=TrustTier.SYSTEM, # Usually system/tool reported
            metadata=metadata or {}
        )
        self._store[item_id] = item
        return item

    def get(self, key: str) -> Optional[MemoryItem]:
        """
        Retrieves the current state.
        Checks TTL/expiry here if needed.
        """
        item_id = f"state::{key}"
        return self._store.get(item_id)

    def search(self, query: str) -> List[MemoryItem]:
        """
        Simple substring search for state variables.
        """
        results = []
        q = query.lower()
        for item in self._store.values():
            if q in item.content.lower() or q in item.id.lower():
                results.append(item)
        return results
